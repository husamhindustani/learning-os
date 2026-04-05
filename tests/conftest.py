"""Shared fixtures for Learning OS tests."""

import pytest
from pathlib import Path
from rich.console import Console


@pytest.fixture
def tmp_workspace(tmp_path):
    """Provide a temporary directory for workspace testing."""
    return tmp_path


@pytest.fixture
def quiet_console():
    """Console that suppresses output during tests."""
    return Console(quiet=True)


SAMPLE_COURSE_YAML = """\
id: test-course
title: "Test Course"
description: "A test course for unit tests."
track: test
type: programming

learning_plan: LEARNING_PLAN.md
exercises: EXERCISES.md

chapters:
  - id: chapter-one
    title: "Chapter One"
    topics:
      - "Topic A"
      - "Topic B"
    exercises_section: "chapter-one"

  - id: chapter-two
    title: "Chapter Two"
    topics:
      - "Topic C"
      - "Topic D"
    exercises_section: "chapter-two"

progress:
  track_name: test
  section_mapping:
    chapter-one: "Chapter One"
    chapter-two: "Chapter Two"
"""


@pytest.fixture
def sample_course(tmp_workspace):
    """Create a valid sample course in a workspace-like structure."""
    course_dir = tmp_workspace / "courses" / "test-course"
    course_dir.mkdir(parents=True)
    (course_dir / "COURSE.yaml").write_text(SAMPLE_COURSE_YAML)
    (course_dir / "LEARNING_PLAN.md").write_text("# Test Course\n\n## Chapter One\n")
    (course_dir / "EXERCISES.md").write_text("# Exercises\n\n## Chapter One\n")
    return course_dir
