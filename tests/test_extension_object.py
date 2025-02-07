from __future__ import annotations

import typing as t

import pytest
import sqlalchemy as sa
from flask import Flask
from werkzeug.exceptions import NotFound

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.record_queries import get_recorded_queries


@pytest.mark.usefixtures("app_ctx")
def test_get_or_404(db: SQLAlchemy, Todo: t.Any) -> None:
    item = Todo()
    db.session.add(item)
    db.session.commit()
    assert db.get_or_404(Todo, 1) is item

    with pytest.raises(NotFound):
        db.get_or_404(Todo, 2)


def test_get_or_404_kwargs(app: Flask) -> None:
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True
    db = SQLAlchemy(app)

    class User(db.Model):
        id = sa.Column(db.Integer, primary_key=True)  # type: ignore[var-annotated]

    class Todo(db.Model):
        id = sa.Column(sa.Integer, primary_key=True)
        user_id = sa.Column(sa.ForeignKey(User.id))  # type: ignore[var-annotated]
        user = db.relationship(User)

    with app.app_context():
        db.create_all()
        db.session.add(Todo(user=User()))
        db.session.commit()

    with app.app_context():
        item = db.get_or_404(Todo, 1, options=[db.joinedload(Todo.user)])
        assert item.user.id == 1
        # one query with join, no second query when accessing relationship
        assert len(get_recorded_queries()) == 1
