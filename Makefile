include .env
export

# source .env
migrate:
	uv run alembic revision --autogenerate -m "$(name)"

upgrade:
	uv run alembic upgrade head

