dev:
	uvicorn main:app --port 6969 --workers 6 --reload

index:
	python3 wrench.py --index
