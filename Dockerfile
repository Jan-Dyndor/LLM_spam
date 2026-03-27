FROM python:3.14-slim

WORKDIR /app 

# RUN mkdir -p /app/data

COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir -e . 

# Poor cache since pyproject.toml-based editable install requires project code.
# Small code changes trigger reinstall of the package layer.
# In a future project, a lockfile / requirements export / uv can improve this.

RUN useradd -m -u 1001 nonroot
RUN chown -R nonroot:nonroot /app
USER nonroot


EXPOSE 8000

CMD ["fastapi", "run", "src/app/main.py", "--port", "8000"]