import pytest


@pytest.mark.asyncio
class TestCollegeCRUD:
    async def test_list_colleges_empty(self, auth_client):
        response = await auth_client.get("/api/v1/colleges")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert "items" in data

    async def test_create_college(self, auth_client, db_session):
        response = await auth_client.post("/api/v1/colleges", json={
            "name": "New Test College",
            "code": "NTC001",
            "college_type": "engineering",
            "academic_year": "2025-2026",
        })
        assert response.status_code in (201, 200)
        data = response.json()
        assert data["name"] == "New Test College"

    async def test_get_college(self, auth_client, seed_college):
        response = await auth_client.get(f"/api/v1/colleges/{seed_college.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == seed_college.name

    async def test_update_college(self, auth_client, seed_college):
        response = await auth_client.put(f"/api/v1/colleges/{seed_college.id}", json={
            "name": "Updated College Name",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated College Name"

    async def test_delete_college(self, auth_client, seed_college, db_session):
        response = await auth_client.delete(f"/api/v1/colleges/{seed_college.id}")
        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_get_nonexistent_college(self, auth_client):
        import uuid
        response = await auth_client.get(f"/api/v1/colleges/{uuid.uuid4()}")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDepartmentCRUD:
    async def test_create_department(self, auth_client, seed_college):
        response = await auth_client.post("/api/v1/departments", json={
            "college_id": str(seed_college.id),
            "name": "Electronics",
            "code": "EC",
        })
        assert response.status_code in (201, 200)
        data = response.json()
        assert data["name"] == "Electronics"

    async def test_list_departments(self, auth_client, seed_department):
        response = await auth_client.get("/api/v1/departments")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1


@pytest.mark.asyncio
class TestTeacherCRUD:
    async def test_create_teacher(self, auth_client, seed_department):
        response = await auth_client.post("/api/v1/teachers", json={
            "department_id": str(seed_department.id),
            "employee_code": "T003",
            "full_name": "Dr. Johnson",
            "email": "johnson@test.edu",
            "max_lectures_per_day": 4,
            "max_lectures_per_week": 20,
        })
        assert response.status_code in (201, 200)
        data = response.json()
        assert data["full_name"] == "Dr. Johnson"


@pytest.mark.asyncio
class TestSubjectCRUD:
    async def test_create_subject(self, auth_client, seed_department):
        response = await auth_client.post("/api/v1/subjects", json={
            "department_id": str(seed_department.id),
            "name": "Data Structures",
            "code": "DS201",
            "subject_type": "theory",
            "lectures_per_week": 4,
        })
        assert response.status_code in (201, 200)


@pytest.mark.asyncio
class TestSectionCRUD:
    async def test_create_section(self, auth_client, seed_semester):
        response = await auth_client.post("/api/v1/sections", json={
            "semester_id": str(seed_semester.id),
            "name": "Section B",
            "code": "CSB",
            "strength": 55,
        })
        assert response.status_code in (201, 200)


@pytest.mark.asyncio
class TestClassroomCRUD:
    async def test_create_classroom(self, auth_client, seed_college):
        response = await auth_client.post("/api/v1/classrooms", json={
            "college_id": str(seed_college.id),
            "name": "Room 201",
            "code": "R201",
            "capacity": 40,
            "building": "East Wing",
            "floor": 2,
            "room_type": "lecture",
        })
        assert response.status_code in (201, 200)


@pytest.mark.asyncio
class TestTimeSlotCRUD:
    async def test_create_time_slot(self, auth_client, seed_college):
        response = await auth_client.post("/api/v1/time-slots", json={
            "college_id": str(seed_college.id),
            "name": "Monday 11-12",
            "day_of_week": "monday",
            "start_time": "11:00",
            "end_time": "12:00",
            "slot_type": "lecture",
        })
        assert response.status_code in (201, 200)


@pytest.mark.asyncio
class TestRoleAuthorization:
    async def test_viewer_cannot_create(self, viewer_client):
        response = await viewer_client.post("/api/v1/colleges", json={
            "name": "Should Fail",
            "code": "FAIL",
            "college_type": "engineering",
            "academic_year": "2025-2026",
        })
        assert response.status_code in (401, 403)

    async def test_viewer_can_read(self, viewer_client, seed_college):
        response = await viewer_client.get(f"/api/v1/colleges/{seed_college.id}")
        assert response.status_code == 200
