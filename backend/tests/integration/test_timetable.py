import pytest


@pytest.mark.asyncio
class TestTimetableFlow:
    async def test_create_timetable(self, auth_client, seed_section, seed_academic_calendar):
        response = await auth_client.post("/api/v1/timetables", json={
            "section_id": str(seed_section.id),
            "academic_calendar_id": str(seed_academic_calendar.id),
            "name": "Test TT",
        })
        assert response.status_code in (201, 200)

    async def test_list_timetables(self, auth_client):
        response = await auth_client.get("/api/v1/timetables")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_get_timetable(self, auth_client, seed_timetable):
        response = await auth_client.get(f"/api/v1/timetables/{seed_timetable.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == seed_timetable.name

    async def test_get_nonexistent_timetable(self, auth_client):
        import uuid
        response = await auth_client.get(f"/api/v1/timetables/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_publish_timetable(self, auth_client, seed_timetable):
        response = await auth_client.post(f"/api/v1/timetables/{seed_timetable.id}/publish")
        assert response.status_code in (200, 400, 422)

    async def test_archive_timetable(self, auth_client, seed_timetable):
        response = await auth_client.post(f"/api/v1/timetables/{seed_timetable.id}/archive")
        assert response.status_code == 200

    async def test_generate_timetable(
        self, auth_client, db_session, seed_timetable, seed_subject_assignment,
        seed_time_slots, seed_working_days, seed_classroom,
    ):
        import uuid
        response = await auth_client.get(f"/api/v1/timetables/{seed_timetable.id}")
        if response.status_code != 200:
            pytest.skip("Timetable not found, skipping generation test")

        response = await auth_client.post(f"/api/v1/timetables/{seed_timetable.id}/generate")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "score" in data
        assert "conflicts" in data
        assert 0 <= data["score"] <= 100


@pytest.mark.asyncio
class TestTimetableEntries:
    async def test_add_entry(self, auth_client, seed_timetable, seed_time_slot, seed_section, seed_teacher, seed_subject):
        response = await auth_client.post(f"/api/v1/timetables/{seed_timetable.id}/entries", json={
            "time_slot_id": str(seed_time_slot.id),
            "section_id": str(seed_section.id),
            "teacher_id": str(seed_teacher.id),
            "subject_id": str(seed_subject.id),
        })
        assert response.status_code in (201, 200)
        if response.status_code == 201:
            data = response.json()
            assert "id" in data

    async def test_list_entries(self, auth_client, seed_timetable):
        response = await auth_client.get(f"/api/v1/timetables/{seed_timetable.id}/entries")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


@pytest.mark.asyncio
class TestConflicts:
    async def test_list_conflicts(self, auth_client, seed_timetable):
        response = await auth_client.get("/api/v1/conflicts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_list_conflicts_by_timetable(self, auth_client, seed_timetable):
        response = await auth_client.get(f"/api/v1/conflicts?timetable_id={seed_timetable.id}")
        assert response.status_code == 200
