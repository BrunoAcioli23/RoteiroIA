from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.tavily import TavilyTools

from agno.storage.sqlite import SqliteStorage
from agno.playground import Playground, serve_playground_app

from dotenv import load_dotenv

from videos_tools import load_transcriptions, format_transcriptions_to_markdown, get_creator_transcriptions, list_available_creators, get_transcripts
from fastapi import Request
from starlette.responses import RedirectResponse

load_dotenv()

copywriter = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    name="copywriter",
    add_history_to_messages=True,
    num_history_runs=3,
    storage=SqliteStorage(
        table_name="agent_sessions",
        db_file="tmp/storage.db"
    ),
    tools=[
        TavilyTools(),
        list_available_creators,
        get_creator_transcriptions
        ],
    show_tool_calls=True,
    instructions=open("prompts/copywriter.md").read()
)

app = Playground(agents=[copywriter]).get_app()

@app.middleware("http")
async def legacy_playground_prefix(request: Request, call_next):
    path = request.scope.get("path", "")
    if path.startswith("/playground/") or path == "/playground/status":

        new_path = "/v1" + path

        if not path.startswith("/v1/"):
            request.scope["path"] = new_path
    return await call_next(request)

@app.get("/playground/status", include_in_schema=False)
async def legacy_status_redirect():
    return RedirectResponse(url="/v1/playground/status", status_code=307)

if __name__ == '__main__':
    serve_playground_app('agent:app', reload=True)