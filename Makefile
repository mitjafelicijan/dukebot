dev:
	uvicorn main:app --port 6969 --workers 6 --reload

server:
	uvicorn main:app --port 6969 --workers 6

index:
	-rm -rf storage/
	python3 wrench.py --index
