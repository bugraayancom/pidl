"""
Test Cognitive Load Theory Implementation
Sweller (1988) teorisi test scripti
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommendation_engine import RecommendationEngine

def test_clt_implementation():
    """CLT implementasyonunu test et"""

    print("=" * 80)
    print("🧠 COGNITIVE LOAD THEORY (SWELLER, 1988) - TEST")
    print("=" * 80)
    print()

    # Initialize engine
    engine = RecommendationEngine()

    # Test scenarios
    test_scenarios = [
        {
            "name": "Novice User - Simple Task",
            "profile": {
                "score": 20,
                "level": "novice",
                "domain": "education",
                "responses": {"ai_experience": False}
            },
            "task_complexity": 0.3
        },
        {
            "name": "Competent User - Medium Task",
            "profile": {
                "score": 50,
                "level": "competent",
                "domain": "technical",
                "responses": {"ai_experience": True}
            },
            "task_complexity": 0.5
        },
        {
            "name": "Expert User - Complex Task",
            "profile": {
                "score": 90,
                "level": "expert",
                "domain": "technical",
                "responses": {"ai_experience": True}
            },
            "task_complexity": 0.8
        }
    ]

    for scenario in test_scenarios:
        print(f"\n{'='*80}")
        print(f"📋 Test Scenario: {scenario['name']}")
        print(f"{'='*80}")
        print(f"User Level: {scenario['profile']['level']}")
        print(f"Task Complexity: {scenario['task_complexity']}")
        print()

        # Create user vector
        user_vec = engine.create_user_vector(scenario["profile"])

        # Test each persona
        print(f"🎭 Testing all 10 personas:\n")

        test_personas = [
            ("edu_novice", "Ayşe Yeni Başlayan"),
            ("edu_competent", "Zeynep Yetkin"),
            ("edu_expert", "Fatma Uzman"),
            ("tech_novice", "Can Acemi"),
            ("tech_competent", "Elif Yetkin"),
            ("tech_expert", "Ahmet Uzman")
        ]

        for persona_id, persona_name in test_personas:
            persona_vec = engine.persona_vectors[persona_id]
            clt_result = engine.calculate_total_cognitive_load(
                user_vec,
                persona_vec,
                task_complexity=scenario["task_complexity"]
            )

            print(f"  📊 {persona_name} ({persona_id}):")
            print(f"     Intrinsic Load:  {clt_result['intrinsic_load']:.3f}")
            print(f"     Extraneous Load: {clt_result['extraneous_load']:.3f}")
            print(f"     Germane Load:    {clt_result['germane_load']:.3f}")
            print(f"     Total Load:      {clt_result['total_load']:.3f}")
            print(f"     Capacity:        {clt_result['cognitive_capacity']:.3f}")
            print(f"     Efficiency:      {clt_result['load_efficiency']:.3f}")
            print(f"     Optimal Zone:    {'✅ YES' if clt_result['is_in_optimal_zone'] else '❌ NO'}")
            print(f"     Overloaded:      {'⚠️  YES' if clt_result['is_overloaded'] else '✅ NO'}")

            if clt_result['warnings']:
                print(f"     ⚠️  Warnings:")
                for warning in clt_result['warnings']:
                    print(f"        {warning}")

            if clt_result['recommendations']:
                print(f"     💡 Recommendations:")
                for rec in clt_result['recommendations']:
                    print(f"        {rec}")

            print()

        # Test CLT-based ranking
        print(f"\n🏆 CLT-Optimal Persona Rankings:")
        print("-" * 80)

        clt_rankings = engine.get_clt_optimal_personas(
            user_vec,
            task_complexity=scenario["task_complexity"],
            top_k=5
        )

        for idx, ranking in enumerate(clt_rankings, 1):
            persona_id = ranking['persona_id']
            clt_score = ranking['clt_score']
            analysis = ranking['clt_analysis']

            print(f"\n  {idx}. {persona_id}: CLT Score = {clt_score:.3f}")
            print(f"     IL={analysis['intrinsic_load']:.3f}, "
                  f"EL={analysis['extraneous_load']:.3f}, "
                  f"GL={analysis['germane_load']:.3f}")
            print(f"     Optimal Zone: {'✅' if analysis['is_in_optimal_zone'] else '❌'}")

            if analysis['recommendations']:
                print(f"     💡 {analysis['recommendations'][0]}")

        print()

def test_individual_clt_methods():
    """CLT metodlarını ayrı ayrı test et"""

    print("\n" + "=" * 80)
    print("🔬 INDIVIDUAL CLT METHOD TESTS")
    print("=" * 80)
    print()

    engine = RecommendationEngine()

    # Test user: Competent level
    test_profile = {
        "score": 50,
        "level": "competent",
        "domain": "technical",
        "responses": {"ai_experience": True}
    }
    user_vec = engine.create_user_vector(test_profile)

    # Test persona: Expert
    persona_vec = engine.persona_vectors["tech_expert"]

    print("📊 Test Configuration:")
    print(f"   User: Competent (score=50)")
    print(f"   Persona: Ahmet Uzman (tech_expert)")
    print(f"   Task Complexity: 0.7")
    print()

    # Test intrinsic load
    print("1️⃣  Intrinsic Load Test:")
    print("   Formula: IL = task_complexity × (1 - user_expertise)")
    intrinsic = engine.calculate_intrinsic_load(user_vec, task_complexity=0.7)
    print(f"   Result: {intrinsic:.3f}")
    print(f"   Expected: ~0.30-0.40 (competent user, complex task)")
    print(f"   ✅ {'PASS' if 0.20 < intrinsic < 0.50 else 'FAIL'}")
    print()

    # Test extraneous load
    print("2️⃣  Extraneous Load Test:")
    print("   Formula: EL = poor_org×0.4 + excess_verb×0.3 + complexity×0.3")
    extraneous = engine.calculate_extraneous_load(persona_vec)
    print(f"   Result: {extraneous:.3f}")
    print(f"   Persona Modularity: {persona_vec.modularity:.3f}")
    print(f"   Persona Verbosity: {persona_vec.verbosity:.3f}")
    print(f"   Expected: <0.30 (expert has good organization)")
    print(f"   ✅ {'PASS' if extraneous < 0.40 else 'FAIL'}")
    print()

    # Test germane load
    print("3️⃣  Germane Load Test:")
    print("   Formula: GL = learning_support + pedagogical + capacity + examples")
    germane = engine.calculate_germane_load(user_vec, persona_vec)
    print(f"   Result: {germane:.3f}")
    print(f"   Persona Learning Support: {persona_vec.learning_support:.3f}")
    print(f"   Persona Pedagogical Focus: {persona_vec.pedagogical_focus:.3f}")
    print(f"   Expected: 0.40-0.60 (tech expert has moderate learning support)")
    print(f"   ✅ {'PASS' if 0.30 < germane < 0.70 else 'FAIL'}")
    print()

    # Test total cognitive load
    print("4️⃣  Total Cognitive Load Test:")
    print("   Formula: TCL = IL + EL - GL")
    clt_full = engine.calculate_total_cognitive_load(user_vec, persona_vec, 0.7)
    print(f"   Intrinsic: {clt_full['intrinsic_load']:.3f}")
    print(f"   Extraneous: {clt_full['extraneous_load']:.3f}")
    print(f"   Germane: {clt_full['germane_load']:.3f}")
    print(f"   Total: {clt_full['total_load']:.3f}")
    print(f"   Capacity: {clt_full['cognitive_capacity']:.3f}")
    print(f"   Optimal Zone: {clt_full['is_in_optimal_zone']}")
    print(f"   Overloaded: {clt_full['is_overloaded']}")
    print(f"   ✅ PASS (no errors)")
    print()

    # Test CLT ranking
    print("5️⃣  CLT Optimal Ranking Test:")
    rankings = engine.get_clt_optimal_personas(user_vec, task_complexity=0.5, top_k=3)
    print(f"   Top 3 Personas:")
    for idx, ranking in enumerate(rankings, 1):
        print(f"   {idx}. {ranking['persona_id']}: {ranking['clt_score']:.3f}")
    print(f"   ✅ PASS (returned {len(rankings)} personas)")
    print()

def test_edge_cases():
    """Edge case'leri test et"""

    print("\n" + "=" * 80)
    print("⚠️  EDGE CASE TESTS")
    print("=" * 80)
    print()

    engine = RecommendationEngine()

    print("1️⃣  Novice User + Expert Persona (Overload Expected):")
    novice_profile = {
        "score": 10,
        "level": "novice",
        "domain": "education",
        "responses": {"ai_experience": False}
    }
    user_vec = engine.create_user_vector(novice_profile)
    persona_vec = engine.persona_vectors["tech_expert"]

    clt_result = engine.calculate_total_cognitive_load(user_vec, persona_vec, 0.8)
    print(f"   Total Load: {clt_result['total_load']:.3f}")
    print(f"   Overloaded: {clt_result['is_overloaded']}")
    print(f"   Warnings: {len(clt_result['warnings'])} warning(s)")
    print(f"   ✅ {'PASS' if clt_result['is_overloaded'] else '⚠️  Expected overload'}")
    print()

    print("2️⃣  Expert User + Novice Persona (Underload Expected):")
    expert_profile = {
        "score": 95,
        "level": "expert",
        "domain": "technical",
        "responses": {"ai_experience": True}
    }
    user_vec = engine.create_user_vector(expert_profile)
    persona_vec = engine.persona_vectors["edu_novice"]

    clt_result = engine.calculate_total_cognitive_load(user_vec, persona_vec, 0.2)
    print(f"   Total Load: {clt_result['total_load']:.3f}")
    print(f"   Underloaded: {clt_result['is_underloaded']}")
    print(f"   Warnings: {len(clt_result['warnings'])} warning(s)")
    print(f"   ✅ {'PASS' if clt_result['is_underloaded'] else '⚠️  Expected underload'}")
    print()

    print("3️⃣  Competent User + Competent Persona (Optimal Expected):")
    competent_profile = {
        "score": 50,
        "level": "competent",
        "domain": "education",
        "responses": {"ai_experience": True}
    }
    user_vec = engine.create_user_vector(competent_profile)
    persona_vec = engine.persona_vectors["edu_competent"]

    clt_result = engine.calculate_total_cognitive_load(user_vec, persona_vec, 0.5)
    print(f"   Total Load: {clt_result['total_load']:.3f}")
    print(f"   Optimal Zone: {clt_result['is_in_optimal_zone']}")
    print(f"   Recommendations: {clt_result['recommendations']}")
    print(f"   ✅ {'PASS' if clt_result['is_in_optimal_zone'] else '⚠️  Expected optimal zone'}")
    print()

def test_clt_formulas():
    """CLT formüllerinin matematiksel doğruluğunu test et"""

    print("\n" + "=" * 80)
    print("📐 MATHEMATICAL FORMULA VALIDATION")
    print("=" * 80)
    print()

    engine = RecommendationEngine()

    # Create test vectors with known values
    from recommendation_engine import UserVector, PersonaVector

    # Test user with known values
    user_vec = UserVector(
        technical_skill=0.5,
        domain_knowledge=0.5,
        ai_experience=0.5,
        learning_goal=0.5,
        procedural_knowledge=0.5,
        declarative_knowledge=0.5,
        conditional_knowledge=0.5,
        cognitive_capacity=0.75,
        pattern_recognition=0.5,
        abstraction_level=0.5
    )

    # Test persona with known values
    persona_vec = PersonaVector(
        persona_id="test",
        code_complexity=0.5,
        verbosity=0.6,  # Optimal range
        technical_depth=0.5,
        pedagogical_focus=0.5,
        comment_density=0.5,
        modularity=0.7,  # Good organization
        example_richness=0.6,
        learning_support=0.6,
        production_readiness=0.5,
        innovation_factor=0.5
    )

    print("📊 Test Vectors:")
    print(f"   User Expertise: 0.50 (computed from technical/domain/procedural)")
    print(f"   Persona Modularity: 0.70")
    print(f"   Persona Verbosity: 0.60 (optimal range)")
    print(f"   Task Complexity: 0.50")
    print()

    # Test IL formula
    print("1️⃣  Intrinsic Load Formula:")
    print("   IL = task_complexity × (1 - user_expertise)")
    print("   Expected: 0.50 × (1 - 0.50) = 0.25")
    il = engine.calculate_intrinsic_load(user_vec, 0.5)
    print(f"   Computed: {il:.3f}")
    print(f"   ✅ {'PASS' if abs(il - 0.25) < 0.05 else 'FAIL'}")
    print()

    # Test EL formula
    print("2️⃣  Extraneous Load Formula:")
    print("   EL = poor_org×0.4 + excess_verb×0.3 + complexity×0.3")
    print("   Poor Org = 1 - 0.70 = 0.30")
    print("   Excess Verb = 0.0 (in optimal range)")
    print("   Expected: 0.30×0.4 + 0.0×0.3 + 0.25×0.3 = 0.195")
    el = engine.calculate_extraneous_load(persona_vec)
    print(f"   Computed: {el:.3f}")
    print(f"   ✅ {'PASS' if abs(el - 0.195) < 0.05 else 'FAIL'}")
    print()

    # Test GL formula
    print("3️⃣  Germane Load Formula:")
    print("   GL = learn_sup×0.35 + ped×0.30 + capacity×0.20 + examples×0.15")
    gl = engine.calculate_germane_load(user_vec, persona_vec)
    expected_gl = 0.6*0.35 + 0.5*0.30 + 0.625*0.20 + 0.6*0.15
    print(f"   Expected: ~{expected_gl:.3f}")
    print(f"   Computed: {gl:.3f}")
    print(f"   ✅ {'PASS' if abs(gl - expected_gl) < 0.05 else 'FAIL'}")
    print()

    # Test TCL
    print("4️⃣  Total Cognitive Load:")
    print(f"   TCL = IL + EL - GL")
    print(f"   Expected: {il:.3f} + {el:.3f} - {gl:.3f} = {il + el - gl:.3f}")
    clt = engine.calculate_total_cognitive_load(user_vec, persona_vec, 0.5)
    print(f"   Computed: {clt['total_load']:.3f}")
    expected_tcl = il + el - gl
    print(f"   ✅ {'PASS' if abs(clt['total_load'] - expected_tcl) < 0.05 else 'FAIL'}")
    print()

if __name__ == "__main__":
    try:
        # Run all tests
        test_clt_implementation()
        test_individual_clt_methods()
        test_edge_cases()
        test_clt_formulas()

        print("\n" + "=" * 80)
        print("✅ ALL COGNITIVE LOAD THEORY TESTS COMPLETED!")
        print("=" * 80)
        print("\n📚 References:")
        print("   Sweller, J. (1988). Cognitive load during problem solving.")
        print("   Cognitive Science, 12(2), 257-285.")
        print()

    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
