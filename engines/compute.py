"""
QFD Computation Engines - HOQ, AHP, Kano
"""
import numpy as np
from collections import defaultdict


class HOQEngine:
    """Quality House computation engine."""

    SYMBOL_MAP = {"●": 9, "◎": 3, "△": 1, "": 0, " ": 0}
    SYMBOL_REVERSE = {9: "●", 3: "◎", 1: "△", 0: ""}
    CORRELATION_SYMBOLS = {
        "strong_positive": "++",
        "positive": "+",
        "negative": "-",
        "strong_negative": "--",
        "": ""
    }

    @staticmethod
    def symbol_to_value(symbol):
        return HOQEngine.SYMBOL_MAP.get(symbol, 0)

    @staticmethod
    def value_to_symbol(value):
        return HOQEngine.SYMBOL_REVERSE.get(int(value), "")

    @staticmethod
    def compute_importance(vocs, ctqs, relationships):
        """
        Compute absolute and relative technical importance for each CTQ.

        Formula (per OpenQFD spec): Tai = Sum(rij * Ii), Ti = Tai / Sum(Tai)
        where Ii is the VOC's raw customer importance rating. improvement_ratio
        and sales_point do NOT factor into Tai/Ti — they only apply to the
        right-wall Wai = Ri * Si * Ii calculation (see HOQMatrixView).

        Args:
            vocs: list of voc dicts with 'id', 'importance'
            ctqs: list of ctq dicts with 'id', 'difficulty'
            relationships: list of relationship dicts with 'voc_id', 'ctq_id', 'strength'

        Returns:
            dict: {ctq_id: {
                'absolute_importance': float,
                'relative_importance': float (percentage),
                'weighted_importance': float (considering difficulty),
                'rank': int
            }}
        """
        # Build relationship lookup
        rel_map = {}
        for r in relationships:
            rel_map[(r['voc_id'], r['ctq_id'])] = r['strength']

        # Build VOC weight map: Tai uses raw importance (Ii) only
        voc_weights = {}
        for v in vocs:
            voc_weights[v['id']] = v.get('importance', 3) or 3

        # Compute absolute importance for each CTQ
        results = {}
        total_abs = 0
        for c in ctqs:
            abs_imp = 0
            for v in vocs:
                strength = rel_map.get((v['id'], c['id']), 0) or 0
                weight = voc_weights.get(v['id'], 0) or 0
                abs_imp += strength * weight
            results[c['id']] = {'absolute_importance': abs_imp}
            total_abs += abs_imp

        # Compute relative importance and weighted importance
        for c in ctqs:
            cid = c['id']
            if total_abs > 0:
                results[cid]['relative_importance'] = (results[cid]['absolute_importance'] / total_abs) * 100
            else:
                results[cid]['relative_importance'] = 0
            # Weighted with difficulty (lower difficulty = higher priority)
            difficulty = c.get('difficulty', 3) or 3
            results[cid]['weighted_importance'] = results[cid]['absolute_importance'] / max(difficulty, 0.1)

        # Compute ranks
        sorted_ctqs = sorted(results.items(), key=lambda x: x[1]['absolute_importance'], reverse=True)
        for rank, (cid, _) in enumerate(sorted_ctqs, 1):
            results[cid]['rank'] = rank

        return results

    @staticmethod
    def compute_row_weights(vocs):
        """Compute adjusted VOC weights (importance * improvement_ratio * sales_point)."""
        weights = {}
        for v in vocs:
            base = v.get('importance', 3) or 3
            ir = v.get('improvement_ratio', 1.0) or 1.0
            sp = v.get('sales_point', 1.0) or 1.0
            weights[v['id']] = base * ir * sp
        total = sum(weights.values())
        normalized = {}
        for vid, w in weights.items():
            normalized[vid] = (w / total * 100) if total > 0 else 0
        return weights, normalized


class AHPEngine:
    """Analytic Hierarchy Process engine."""

    # Random consistency index
    RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
          7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49, 11: 1.51,
          12: 1.54, 13: 1.56, 14: 1.57, 15: 1.59}

    @staticmethod
    def compute_weights(comparison_matrix):
        """
        Compute priority weights from pairwise comparison matrix.

        Args:
            comparison_matrix: numpy array (n x n)

        Returns:
            dict with 'weights', 'lambda_max', 'ci', 'cr', 'consistent'
        """
        n = comparison_matrix.shape[0]
        if n < 2:
            return {'weights': np.array([1.0]), 'lambda_max': 1.0,
                    'ci': 0.0, 'cr': 0.0, 'consistent': True}

        # Geometric mean method (more robust)
        geo_means = np.prod(comparison_matrix, axis=1) ** (1.0 / n)
        weights = geo_means / geo_means.sum()

        # Compute consistency
        weighted_sum = comparison_matrix @ weights
        lambda_max = np.mean(weighted_sum / weights)
        ci = (lambda_max - n) / (n - 1) if n > 1 else 0

        ri = AHPEngine.RI.get(n, 1.59)
        cr = ci / ri if ri > 0 else 0

        return {
            'weights': weights,
            'lambda_max': lambda_max,
            'ci': ci,
            'cr': cr,
            'consistent': cr < 0.1
        }

    @staticmethod
    def build_matrix(n, comparisons):
        """
        Build comparison matrix from pairwise comparisons.

        Args:
            n: matrix size
            comparisons: dict {(i,j): value} where i < j

        Returns:
            numpy array (n x n)
        """
        matrix = np.ones((n, n))
        for (i, j), v in comparisons.items():
            matrix[i][j] = v
            matrix[j][i] = 1.0 / v if v != 0 else 1.0
        return matrix

    @staticmethod
    def suggest_fix(matrix, cr_target=0.1):
        """Suggest which comparison to adjust to improve consistency."""
        n = matrix.shape[0]
        if n < 3:
            return None

        result = AHPEngine.compute_weights(matrix)
        if result['consistent']:
            return None

        weights = result['weights']
        max_deviation = 0
        worst_pair = (0, 1)

        for i in range(n):
            for j in range(i + 1, n):
                ideal = weights[i] / weights[j]
                actual = matrix[i][j]
                deviation = abs(np.log(actual) - np.log(ideal)) if actual > 0 and ideal > 0 else 0
                if deviation > max_deviation:
                    max_deviation = deviation
                    worst_pair = (i, j)

        ideal_value = weights[worst_pair[0]] / weights[worst_pair[1]]
        return {
            'pair': worst_pair,
            'current_value': matrix[worst_pair[0]][worst_pair[1]],
            'suggested_value': round(ideal_value, 2)
        }


class KanoEngine:
    """Kano model analysis engine."""

    TYPES = {
        'M': ('基本型 (Must-be)', '#E74C3C'),
        'O': ('期望型 (One-dimensional)', '#3498DB'),
        'A': ('魅力型 (Attractive)', '#2ECC71'),
        'I': ('无差异型 (Indifferent)', '#95A5A6'),
        'R': ('逆向型 (Reverse)', '#E67E22'),
    }

    @staticmethod
    def classify(functional_score, dysfunctional_score):
        """
        Classify a requirement based on Kano evaluation.

        Args:
            functional_score: average score for functional question (1-5)
            dysfunctional_score: average score for dysfunctional question (1-5)

        Returns:
            str: Kano type code ('M', 'O', 'A', 'I', 'R')
        """
        f = functional_score
        d = dysfunctional_score
        if f >= 3.5 and d <= 2.5:
            return 'A'  # Attractive
        elif f >= 3.5 and d >= 3.5:
            return 'O'  # One-dimensional
        elif f <= 2.5 and d >= 3.5:
            return 'M'  # Must-be
        elif f <= 2.5 and d <= 2.5:
            return 'I'  # Indifferent
        else:
            return 'R'  # Reverse / Questionable

    @staticmethod
    def importance_multiplier(kano_type):
        """Return importance weight multiplier based on Kano type."""
        multipliers = {
            'M': 1.5,   # Must-be: high weight
            'O': 1.2,   # One-dimensional: moderate boost
            'A': 1.0,   # Attractive: standard
            'I': 0.5,   # Indifferent: reduce weight
            'R': 0.3,   # Reverse: significantly reduce
        }
        return multipliers.get(kano_type, 1.0)

    @staticmethod
    def get_type_label(kano_type):
        if kano_type in KanoEngine.TYPES:
            return KanoEngine.TYPES[kano_type][0]
        return '未分类'

    @staticmethod
    def get_type_color(kano_type):
        if kano_type in KanoEngine.TYPES:
            return KanoEngine.TYPES[kano_type][1]
        return '#BDC3C7'
