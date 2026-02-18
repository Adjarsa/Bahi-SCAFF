from app.services.scaffolding import ScaffoldingService


def test_scaffolding_dimensions_are_within_standard_limits() -> None:
    service = ScaffoldingService()
    plan = service.compute_plan(facade_width_m=18.0, facade_height_m=12.0, terrain_factor=1.0)

    assert plan.bays
    assert len(plan.bays) == 6
    assert all(1.5 <= bay.width_m <= 3.0 for bay in plan.bays)
    assert plan.bays[0].levels_m[-1] == 12.0
    assert any("R408" in note for note in plan.compliance_notes)
