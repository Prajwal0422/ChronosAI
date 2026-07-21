import pytest
from datetime import time

from app.domain.value_objects.email import Email
from app.domain.value_objects.phone import Phone
from app.domain.value_objects.time_range import TimeRange


class TestEmail:
    def test_valid_email(self):
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_valid_email_with_plus(self):
        email = Email("test+label@example.co.uk")
        assert email.value == "test+label@example.co.uk"

    def test_email_is_lowercased(self):
        email = Email("Test@Example.COM")
        assert email.value == "test@example.com"

    def test_email_is_stripped(self):
        email = Email("  test@example.com  ")
        assert email.value == "test@example.com"

    def test_invalid_email_no_at(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("notanemail")

    def test_invalid_email_no_domain(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@")

    def test_invalid_email_too_long(self):
        long_local = "a" * 256
        with pytest.raises(ValueError, match="Email must not exceed"):
            Email(f"{long_local}@example.com")

    def test_email_equality(self):
        e1 = Email("test@example.com")
        e2 = Email("test@example.com")
        assert e1 == e2

    def test_email_hashing(self):
        e1 = Email("test@example.com")
        e2 = Email("test@example.com")
        assert hash(e1) == hash(e2)

    def test_email_str(self):
        email = Email("test@example.com")
        assert str(email) == "test@example.com"


class TestPhone:
    def test_valid_phone(self):
        phone = Phone("+12345678901")
        assert phone.value == "+12345678901"

    def test_valid_phone_without_plus(self):
        phone = Phone("12345678901")
        assert phone.value == "12345678901"

    def test_phone_is_stripped(self):
        phone = Phone("  +12345678901  ")
        assert phone.value == "+12345678901"

    def test_invalid_phone_too_short(self):
        with pytest.raises(ValueError, match="Invalid phone number"):
            Phone("+123")

    def test_invalid_phone_too_long(self):
        with pytest.raises(ValueError, match="Invalid phone number"):
            Phone("+" + "1" * 16)

    def test_invalid_phone_with_letters(self):
        with pytest.raises(ValueError, match="Invalid phone number"):
            Phone("+1234abc567")

    def test_phone_equality(self):
        p1 = Phone("+12345678901")
        p2 = Phone("+12345678901")
        assert p1 == p2

    def test_phone_str(self):
        phone = Phone("+12345678901")
        assert str(phone) == "+12345678901"


class TestTimeRange:
    def test_valid_time_range(self):
        tr = TimeRange(time(9, 0), time(10, 0))
        assert tr.start == time(9, 0)
        assert tr.end == time(10, 0)

    def test_invalid_time_range_equal(self):
        with pytest.raises(ValueError, match="start_time must be before end_time"):
            TimeRange(time(10, 0), time(10, 0))

    def test_invalid_time_range_reversed(self):
        with pytest.raises(ValueError, match="start_time must be before end_time"):
            TimeRange(time(10, 0), time(9, 0))

    def test_overlap_detection(self):
        tr1 = TimeRange(time(9, 0), time(10, 0))
        tr2 = TimeRange(time(9, 30), time(10, 30))
        assert tr1.overlaps(tr2) is True

    def test_no_overlap(self):
        tr1 = TimeRange(time(9, 0), time(10, 0))
        tr2 = TimeRange(time(10, 0), time(11, 0))
        assert tr1.overlaps(tr2) is False

    def test_contained_range_overlaps(self):
        tr1 = TimeRange(time(9, 0), time(11, 0))
        tr2 = TimeRange(time(9, 30), time(10, 0))
        assert tr1.overlaps(tr2) is True

    def test_duration_minutes(self):
        tr = TimeRange(time(9, 0), time(10, 30))
        assert tr.duration_minutes() == 90

    def test_duration_minutes_one_hour(self):
        tr = TimeRange(time(9, 0), time(10, 0))
        assert tr.duration_minutes() == 60

    def test_time_range_equality(self):
        tr1 = TimeRange(time(9, 0), time(10, 0))
        tr2 = TimeRange(time(9, 0), time(10, 0))
        assert tr1 == tr2

    def test_time_range_str(self):
        tr = TimeRange(time(9, 0), time(10, 0))
        assert "09:00:00-10:00:00" in str(tr)
