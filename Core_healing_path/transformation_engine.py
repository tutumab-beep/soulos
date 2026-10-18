"""
Automatic Transformation Engine for SoulOS.

Compares user's state at the beginning of the flow with the state at the end
to automatically detect and categorize transformation.
"""

from datetime import datetime
from .models import Transformation, TRANSFORMATION_TYPES, TRANSFORMATION_STRENGTH


class TransformationEngine:
    """
    Analyzes a completed transformation journey and generates:
    - Transformation type classification
    - Transformation summary
    - Transformation score (weighted)
    - Transformation strength level
    """

    def __init__(self, transformation: Transformation):
        self.transformation = transformation
        self.initial = self._get_initial_state()
        self.final = self._get_final_state()

    def _get_initial_state(self) -> dict:
        """Capture initial state from Tension Observer and Awareness Lens."""
        tension = self.transformation.tension
        awareness = self.transformation.awareness

        return {
            "trigger": tension.trigger if tension else "",
            "intensity": tension.intensity if tension else 0,
            "observation": tension.entry if tension else "",
            "emotion": awareness.emotion if awareness else "",
            "awareness_type": awareness.awareness_type if awareness else "",
            "awareness_entry": awareness.entry if awareness else "",
        }

    def _get_final_state(self) -> dict:
        """Capture final state from all completed stages."""
        belief = self.transformation.belief
        thought = self.transformation.thought
        faith = self.transformation.faith
        celebration = self.transformation.celebration

        return {
            "reframe": belief.reframe if belief else "",
            "affirmation": belief.custom_affirmation if belief else "",
            "limiting_belief": belief.limiting_belief if belief else "",
            "thought_insight": thought.entry if thought else "",
            "thought_intensity": thought.intensity if thought else 0,
            "coping_strategy": thought.coping_strategy if thought else "",
            "faith_reflection": faith.entry if faith else "",
            "ritual": faith.ritual if faith else "",
            "joy": celebration.entry if celebration else "",
            "gratitude": celebration.clarity_notes if celebration else "",
            "clarity_insight": celebration.entry if celebration else "",
        }

    def analyze(self) -> dict:
        """
        Run full transformation analysis and return results.
        """
        results = {
            "transformation_type": self._detect_transformation_type(),
            "transformation_summary": self._generate_summary(),
            "transformation_score": self._calculate_score(),
            "transformation_strength": self._determine_strength(),
            "analyzed_at": datetime.now(),
        }
        return results

    def _detect_transformation_type(self) -> str:
        """
        Detect the primary transformation type based on the journey data.
        Returns the key from TRANSFORMATION_TYPES.
        """
        initial = self.initial
        final = self.final

        # Check for Belief Shift - presence of reframe/affirmation
        if final["reframe"] or final["affirmation"]:
            return "belief_shift"

        # Check for Awareness - awareness_type was identified
        if initial["awareness_type"] in ["thought", "emotion"]:
            return "awareness"

        # Check for Courage - faced high intensity tension
        if initial["intensity"] >= 7:
            return "courage"

        # Check for Emotional Growth - emotion was named and processed
        if initial["emotion"] and final["faith_reflection"]:
            return "emotional_growth"

        # Check for Gratitude - gratitude notes present
        if final["gratitude"]:
            return "gratitude"

        # Check for Self-Trust - coping strategy used, ritual practiced
        if final["coping_strategy"] or final["ritual"]:
            return "self_trust"

        # Check for Acceptance - intensity reduced or perspective shifted
        if (
            final["thought_insight"]
            and initial["intensity"] > final["thought_intensity"]
        ):
            return "acceptance"

        # Check for Action - action commitment or intentional response
        if final["coping_strategy"] or final["ritual"]:
            return "action"

        # Default to awareness if journey was started
        return "awareness"

    def _generate_summary(self) -> str:
        """
        Generate a human-readable transformation summary.
        Format: "✅ [Action] [what changed]"
        """
        initial = self.initial
        final = self.final
        t_type = self._detect_transformation_type()

        # Build "Before" snapshot
        before_parts = []
        if initial["emotion"]:
            before_parts.append(initial["emotion"].capitalize())
        if initial["observation"]:
            # Extract key phrase from observation
            obs = initial["observation"][:50]
            if len(initial["observation"]) > 50:
                obs += "..."
            before_parts.append(obs)
        if initial["intensity"]:
            before_parts.append(f"Intensity {initial['intensity']}/10")

        before_str = "; ".join(before_parts) if before_parts else "Tension"

        # Build "After" snapshot
        after_parts = []
        if final["reframe"]:
            after_parts.append("Reframed belief")
        if final["affirmation"]:
            after_parts.append("New affirmation")
        if final["clarity_insight"]:
            insight = final["clarity_insight"][:50]
            if len(final["clarity_insight"]) > 50:
                insight += "..."
            after_parts.append(insight)
        if final["gratitude"]:
            after_parts.append("Gratitude expressed")
        if final["joy"]:
            after_parts.append("Joy found")

        after_str = "; ".join(after_parts) if after_parts else "New perspective"

        # Generate type-specific summary
        summaries = {
            "awareness": f"✅ Faced {initial['emotion'] or 'tension'} with awareness.",
            "courage": f"✅ Chose courage over {initial['emotion'] or 'fear'} at intensity {initial['intensity']}/10.",
            "emotional_growth": f"✅ Processed {initial['emotion'] or 'emotion'} through reflection and ritual.",
            "belief_shift": f"✅ Replaced '{initial['observation'][:30] if initial['observation'] else 'limiting belief'}' with a healthier perspective.",
            "gratitude": "✅ Cultivated gratitude as a pathway through difficulty.",
            "self_trust": "✅ Trusted inner wisdom to choose a coping strategy.",
            "acceptance": f"✅ Accepted {initial['emotion'] or 'the experience'} without resistance.",
            "action": "✅ Took intentional action despite discomfort.",
        }

        base_summary = summaries.get(t_type, "✅ Completed a transformation journey.")

        # Add before/after context
        return f"Before: {before_str}\nAfter: {after_str}\n\n{base_summary}"

    def _calculate_score(self) -> int:
        """
        Calculate weighted transformation score (0-100).
        Base: stages completed (max 60 points)
        Bonuses: depth indicators (max 40 points)
        """
        score = 0
        initial = self.initial
        final = self.final

        # Base score: stages completed (10 points each, max 60)
        stages_completed = self.transformation.stages_completed
        score += min(stages_completed * 10, 60)

        # Bonus: Initial tension intensity (higher intensity = more transformation potential)
        if initial["intensity"] >= 8:
            score += 10
        elif initial["intensity"] >= 5:
            score += 5

        # Bonus: Awareness type identified
        if initial["awareness_type"] in ["thought", "emotion"]:
            score += 5

        # Bonus: Belief reframe/affirmation present
        if final["reframe"] or final["affirmation"]:
            score += 10

        # Bonus: Thought analysis with coping strategy
        if final["thought_insight"] and final["coping_strategy"]:
            score += 5

        # Bonus: Faith cycle with ritual and reflection
        if final["faith_reflection"] and final["ritual"]:
            score += 5

        # Bonus: Gratitude expressed
        if final["gratitude"]:
            score += 5

        # Bonus: Joy/celebration noted
        if final["joy"]:
            score += 5

        return min(score, 100)

    def _determine_strength(self) -> str:
        """
        Determine transformation strength level based on score.
        """
        score = self._calculate_score()
        if score >= 80:
            return "breakthrough"
        elif score >= 55:
            return "expanding"
        elif score >= 30:
            return "growing"
        else:
            return "seed"

    def apply_results(self) -> Transformation:
        """
        Apply analysis results to the transformation object and save.
        """
        results = self.analyze()
        self.transformation.transformation_type = results["transformation_type"]
        self.transformation.transformation_summary = results["transformation_summary"]
        self.transformation.transformation_score = results["transformation_score"]
        self.transformation.transformation_strength = results["transformation_strength"]
        self.transformation.auto_analyzed_at = results["analyzed_at"]
        self.transformation.save()
        return self.transformation


def analyze_transformation(transformation: Transformation) -> Transformation:
    """
    Convenience function to analyze a transformation.
    """
    engine = TransformationEngine(transformation)
    return engine.apply_results()


def analyze_all_user_transformations(user) -> int:
    """
    Analyze all completed transformations for a user that haven't been analyzed yet.
    Returns count of transformations analyzed.
    """
    transformations = Transformation.objects.filter(
        user=user,
        status="finished",
        auto_analyzed_at__isnull=True,
    )
    count = 0
    for t in transformations:
        if t.stages_completed >= 3:  # Only analyze if substantial progress
            analyze_transformation(t)
            count += 1
    return count
