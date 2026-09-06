import os
import reflex as rx
from mi_agent_007.router import execute as execute_route
from mi_agent_007.router import provider_health


# ============================================================
# MI BOND / AGENT 007
# V2 Control Plane
# ============================================================


NAV_ITEMS = [
    ("layout-dashboard", "Command Center"),
    ("messages-square", "Chats"),
    ("bot", "Agents"),
    ("list-checks", "Tasks"),
    ("workflow", "Automations"),
    ("shield-check", "Approvals"),
    ("brain", "Memory"),
    ("plug", "Connections"),
    ("cpu", "Compute"),
    ("activity", "Activity"),
    ("settings", "Settings"),
]


class State(rx.State):
    page: str = "Command Center"

    username: str = "fady.khella"
    password: str = ""
    authenticated: bool = False
    login_error: str = ""
    remember_device: bool = True

    _expected_username: str = os.getenv("MI_BOND_USERNAME", "fady.khella")
    _expected_password: str = os.getenv("MI_BOND_PASSWORD", "")

    command: str = ""
    last_command: str = ""
    execution_status: str = "Ready"
    last_response: str = ""
    worker_status: str = "UNKNOWN"
    provider_summary: str = "Not checked"
    active_model: str = "Qwen2.5-1.5B-Instruct"
    active_runtime: str = "vLLM"
    active_compute: str = "Kaggle T4"
    mission_count: int = 0
    task_count: int = 0
    approval_count: int = 0

    selected_agent: str = "Bond"

    selected_provider: str = "Auto"
    selected_model: str = "Auto"
    selected_runtime: str = "Auto"

    selected_compute: str = "Auto"
    routing_policy: str = "Balanced"

    max_tokens: str = "4096"
    temperature: str = "0.4"

    approval_mode: str = "Recommended"
    memory_enabled: bool = True

    # --------------------------------------------------------
    # UI state setters
    # --------------------------------------------------------

    def set_page(self, value: str):
        self.page = value

    def set_command(self, value: str):
        self.command = value

    def set_selected_agent(self, value: str):
        self.selected_agent = value

    def set_selected_provider(self, value: str):
        self.selected_provider = value

    def set_selected_model(self, value: str):
        self.selected_model = value

    def set_selected_runtime(self, value: str):
        self.selected_runtime = value

    def set_selected_compute(self, value: str):
        self.selected_compute = value

    def set_routing_policy(self, value: str):
        self.routing_policy = value

    def set_max_tokens(self, value: str):
        self.max_tokens = value

    def set_temperature(self, value: str):
        self.temperature = value

    def set_approval_mode(self, value: str):
        self.approval_mode = value

    def toggle_memory(self, value: bool):
        self.memory_enabled = value

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    def set_username(self, value: str):
        self.username = value

    def set_password(self, value: str):
        self.password = value

    def set_remember_device(self, value: bool):
        self.remember_device = value

    def login(self):
        if (
            self.username.strip() == self._expected_username
            and self.password == self._expected_password
            and bool(self._expected_password)
        ):
            self.authenticated = True
            self.login_error = ""
            self.password = ""
        else:
            self.authenticated = False
            self.login_error = "Access denied. Check your credentials."

    def logout(self):
        self.authenticated = False
        self.password = ""

    # --------------------------------------------------------
    # Execution
    # --------------------------------------------------------

    async def refresh_providers(self):
        self.worker_status = "CHECKING"
        self.provider_summary = "Checking available providers..."

        try:
            health = await provider_health()

            parts = []

            if health.get("kaggle"):
                parts.append("Kaggle")
            if health.get("openai"):
                parts.append("OpenAI")
            if health.get("anthropic"):
                parts.append("Claude")
            if health.get("xai"):
                parts.append("Grok")
            if health.get("ollama"):
                parts.append("Ollama")

            if health.get("kaggle"):
                self.worker_status = "ONLINE"
            elif parts:
                self.worker_status = "FALLBACK"
            else:
                self.worker_status = "OFFLINE"

            self.provider_summary = (
                " · ".join(parts)
                if parts
                else "No inference providers available"
            )

        except Exception as exc:
            self.worker_status = "OFFLINE"
            self.provider_summary = f"Provider check failed: {exc}"

    async def execute(self):
        prompt = self.command.strip()

        if not prompt:
            return

        self.last_command = prompt
        self.last_response = ""
        self.mission_count += 1

        self.worker_status = "ROUTING"
        self.execution_status = (
            f"Routing mission · {self.selected_agent} · "
            f"{self.selected_model} · "
            f"{self.selected_runtime} · "
            f"{self.selected_compute}"
        )

        try:
            try:
                temperature = float(self.temperature)
            except Exception:
                temperature = 0.4

            try:
                max_tokens = int(self.max_tokens)
            except Exception:
                max_tokens = 800

            result = await execute_route(
                prompt=prompt,
                agent=self.selected_agent,
                selected_model=self.selected_model,
                selected_runtime=self.selected_runtime,
                selected_compute=self.selected_compute,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            self.last_response = result.text

            self.active_model = result.model
            self.active_runtime = result.runtime
            self.active_compute = result.compute

            self.worker_status = "ONLINE"

            self.execution_status = (
                f"Completed · {result.provider} · "
                f"{result.model} · "
                f"{result.runtime} · "
                f"{result.compute}"
            )

            self.provider_summary = result.provider

        except Exception as exc:
            self.last_response = (
                "Agent 007 could not obtain an inference route.\n\n"
                f"{exc}"
            )
            self.worker_status = "OFFLINE"
            self.execution_status = "No inference route available"

        self.command = ""


# ============================================================
# COMMON COMPONENTS
# ============================================================


def status_dot(status: str = "online"):
    dot_color = {
        "online": rx.color("green", 9),
        "standby": rx.color("amber", 9),
        "offline": rx.color("gray", 8),
        "future": rx.color("purple", 8),
    }.get(status, rx.color("gray", 8))

    return rx.box(
        width="8px",
        height="8px",
        border_radius="999px",
        background=dot_color,
        flex_shrink="0",
    )


def section_title(kicker: str, title: str, subtitle: str):
    return rx.vstack(
        rx.text(
            kicker.upper(),
            font_size="8px",
            color=rx.color("gray", 10),
            letter_spacing="0.10em",
        ),
        rx.heading(title, size="7"),
        rx.text(
            subtitle,
            color=rx.color("gray", 10),
            max_width="850px",
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def metric(title: str, value: str, detail: str, icon: str):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=16),
                rx.text(
                    title.upper(),
                    size="1",
                    color=rx.color("gray", 10),
                ),
                width="100%",
            ),
            rx.text(value, weight="bold", size="5"),
            rx.text(
                detail,
                size="1",
                color=rx.color("gray", 10),
            ),
            spacing="2",
            align="start",
        ),
        min_width="185px",
        flex="1",
    )


def setting_select(label: str, value, options, handler, description=""):
    return rx.vstack(
        rx.text(label, weight="medium", size="2"),
        rx.select(
            options,
            value=value,
            on_change=handler,
            width="100%",
        ),
        rx.cond(
            description != "",
            rx.text(
                description,
                size="1",
                color=rx.color("gray", 10),
            ),
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def nav_button(icon: str, label: str):
    return rx.button(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(label, size="2", weight="medium"),
            width="100%",
            spacing="3",
        ),
        on_click=State.set_page(label),
        width="100%",
        justify_content="flex-start",
        variant="ghost",
        color_scheme="gray",
        background=rx.cond(
            State.page == label,
            rx.color("gray", 4),
            "transparent",
        ),
    )


def sidebar():
    return rx.vstack(
        rx.hstack(
            rx.image(
                src="/mi-bond-favicon.svg",
                width="32px",
                height="32px",
            ),
            rx.vstack(
                rx.text("MI BOND", weight="bold", size="3"),
                rx.text(
                    "AGENT 007",
                    size="1",
                    color=rx.color("gray", 10),
                    letter_spacing=".14em",
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            padding="4px 7px 18px",
            align="center",
        ),

        nav_button("layout-dashboard", "Command Center"),
        nav_button("messages-square", "Chats"),
        nav_button("bot", "Agents"),
        nav_button("list-checks", "Tasks"),
        nav_button("workflow", "Automations"),
        nav_button("shield-check", "Approvals"),
        nav_button("brain", "Memory"),
        nav_button("plug", "Connections"),
        nav_button("cpu", "Compute"),
        nav_button("activity", "Activity"),

        rx.spacer(),

        rx.card(
            rx.vstack(
                rx.hstack(
                    status_dot("online"),
                    rx.text(
                        "AGENT 007",
                        weight="bold",
                        size="2",
                    ),
                    rx.spacer(),
                    rx.badge(
                        State.worker_status,
                        size="1",
                        variant="soft",
                    ),
                    width="100%",
                ),
                rx.text(
                    State.active_model,
                    size="1",
                    color=rx.color("gray", 10),
                ),
                rx.text(
                    State.active_compute
                    + " · "
                    + State.active_runtime,
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            padding="10px",
            width="100%",
        ),

        nav_button("settings", "Settings"),

        rx.hstack(
            rx.color_mode.button(),
            rx.text(
                "Appearance",
                size="1",
                color=rx.color("gray", 10),
            ),
            rx.spacer(),
            rx.button(
                "Logout",
                size="1",
                variant="ghost",
                on_click=State.logout,
            ),
            width="100%",
            padding="7px",
            align="center",
        ),

        width="250px",
        min_width="250px",
        height="100vh",
        padding="18px 12px",
        border_right="1px solid",
        border_color=rx.color("gray", 5),
        align="stretch",
        position="sticky",
        top="0",
    )


def page_shell(content):
    return rx.box(
        content,
        width="100%",
        min_height="100vh",
    )


# ============================================================
# COMMAND CENTER
# ============================================================


def command_center():
    return rx.vstack(

        rx.hstack(
            section_title(
                "Command Center",
                "MI BOND",
                "Plan, reason, route and execute missions through Agent 007.",
            ),
            rx.spacer(),
            rx.badge(
                rx.hstack(
                    status_dot("online"),
                    rx.text("CONTROL PLANE ONLINE"),
                ),
                variant="soft",
                size="2",
            ),
            width="100%",
            align="start",
        ),

        rx.grid(
            metric(
                "Control Plane",
                "ONLINE",
                "Reflex Cloud · Agent 007",
                "server",
            ),
            metric(
                "Compute",
                State.active_compute,
                "Current inference route",
                "cpu",
            ),
            metric(
                "Runtime",
                State.active_runtime,
                State.active_model,
                "brain",
            ),
            metric(
                "Missions",
                State.mission_count,
                "Executed this session",
                "crosshair",
            ),
            columns="4",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(

                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "Mission Control",
                            size="5",
                            weight="bold",
                        ),
                        rx.text(
                            "Tell Bond what must be accomplished. "
                            "Agent 007 will reason, route and execute.",
                            size="2",
                            color=rx.color("gray", 10),
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.badge(
                        State.routing_policy,
                        variant="soft",
                    ),
                    width="100%",
                ),

                rx.text_area(
                    placeholder=(
                        "Research, analyze, build, monitor, "
                        "schedule, investigate or execute..."
                    ),
                    value=State.command,
                    on_change=State.set_command,
                    min_height="145px",
                    width="100%",
                    size="3",
                ),

                rx.grid(
                    setting_select(
                        "Agent",
                        State.selected_agent,
                        [
                            "Bond",
                            "Research",
                            "Executive",
                            "Engineering",
                            "Communications",
                        ],
                        State.set_selected_agent,
                    ),
                    setting_select(
                        "Model",
                        State.selected_model,
                        [
                            "Auto",
                            "Qwen2.5-1.5B-Instruct",
                            "Qwen2.5-1.5B-Instruct",
                            "OpenAI API",
                            "Claude API",
                            "Grok API",
                            "Local Ollama",
                        ],
                        State.set_selected_model,
                    ),
                    setting_select(
                        "Runtime",
                        State.selected_runtime,
                        [
                            "Auto",
                            "vLLM",
                            "Transformers",
                            "MLX",
                            "Ollama",
                            "Provider API",
                        ],
                        State.set_selected_runtime,
                    ),
                    setting_select(
                        "Compute",
                        State.selected_compute,
                        [
                            "Auto",
                            "Kaggle T4 x2",
                            "Mac Apple Silicon",
                            "Lightning GPU",
                            "Reflex CPU",
                            "NVIDIA CUDA Lab",
                            "AMD ROCm Lab",
                        ],
                        State.set_selected_compute,
                    ),
                    columns="4",
                    spacing="3",
                    width="100%",
                ),

                rx.hstack(
                    rx.hstack(
                        rx.icon("shield-check", size=15),
                        rx.text(
                            "Sensitive external actions require approval.",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("send", size=16),
                        "Execute Mission",
                        on_click=State.execute,
                        size="3",
                    ),
                    width="100%",
                    align="center",
                ),

                spacing="4",
                width="100%",
            ),
            padding="24px",
            width="100%",
        ),

        rx.cond(
            State.last_command != "",
            rx.vstack(

                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.badge("MISSION", variant="soft"),
                            rx.text(
                                "Operator",
                                weight="bold",
                                size="2",
                            ),
                            rx.spacer(),
                            rx.text(
                                "YOU",
                                size="1",
                                color=rx.color("gray", 10),
                            ),
                            width="100%",
                        ),
                        rx.text(
                            State.last_command,
                            white_space="pre-wrap",
                            line_height="1.6",
                            size="2",
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    padding="20px",
                ),

                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.image(
                                src="/mi-bond-favicon.svg",
                                width="28px",
                                height="28px",
                            ),
                            rx.vstack(
                                rx.text(
                                    "AGENT 007",
                                    weight="bold",
                                    size="2",
                                ),
                                rx.text(
                                    State.active_model
                                    + " · "
                                    + State.active_runtime
                                    + " · "
                                    + State.active_compute,
                                    size="1",
                                    color=rx.color("gray", 10),
                                ),
                                spacing="0",
                                align="start",
                            ),
                            rx.spacer(),
                            rx.badge(
                                State.worker_status,
                                variant="soft",
                            ),
                            width="100%",
                        ),

                        rx.divider(),

                        rx.cond(
                            State.last_response != "",
                            rx.text(
                                State.last_response,
                                white_space="pre-wrap",
                                line_height="1.75",
                                size="2",
                            ),
                            rx.hstack(
                                rx.spinner(size="2"),
                                rx.text(
                                    "Agent 007 is reasoning...",
                                    color=rx.color("gray", 10),
                                ),
                                spacing="3",
                            ),
                        ),

                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    padding="22px",
                ),

                spacing="3",
                width="100%",
            ),
        ),

        rx.grid(

            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("activity", size=18),
                        rx.text(
                            "EXECUTION TRACE",
                            weight="bold",
                        ),
                        rx.spacer(),
                        rx.badge(
                            State.worker_status,
                            variant="soft",
                        ),
                        width="100%",
                    ),

                    rx.divider(),

                    rx.hstack(
                        status_dot("online"),
                        rx.text(
                            State.execution_status,
                            size="2",
                        ),
                    ),

                    rx.vstack(
                        rx.text(
                            "ACTIVE ROUTE",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        rx.text(
                            "Agent 007 → "
                            + State.active_model
                            + " → "
                            + State.active_runtime
                            + " → "
                            + State.active_compute,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),

                    rx.text(
                        "Tool calls, approvals, retries, tokens, "
                        "latency and artifacts will appear here "
                        "as those execution layers are enabled.",
                        size="1",
                        color=rx.color("gray", 10),
                    ),

                    spacing="3",
                    align="start",
                    width="100%",
                ),
                padding="20px",
            ),

            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("cpu", size=18),
                        rx.text(
                            "COMPUTE FABRIC",
                            weight="bold",
                        ),
                    ),

                    rx.divider(),

                    compute_row(
                        "Reflex Cloud",
                        "Persistent control plane",
                        "online",
                    ),

                    compute_row(
                        "Kaggle",
                        "NVIDIA T4 ×2 · vLLM worker",
                        "online",
                    ),

                    compute_row(
                        "Mac",
                        "Apple Silicon · MLX / Ollama",
                        "standby",
                    ),

                    compute_row(
                        "Lightning",
                        "Optional GPU fallback",
                        "standby",
                    ),

                    compute_row(
                        "CUDA / ROCm Labs",
                        "Engineering workers",
                        "standby",
                    ),

                    spacing="3",
                    align="start",
                    width="100%",
                ),
                padding="20px",
            ),

            columns="2",
            spacing="3",
            width="100%",
        ),

        width="100%",
        max_width="1500px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# COMPUTE
# ============================================================


def compute_row(name: str, description: str, status: str):
    return rx.hstack(
        status_dot(status),
        rx.vstack(
            rx.text(name, weight="medium", size="2"),
            rx.text(
                description,
                size="1",
                color=rx.color("gray", 10),
            ),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.badge(status.upper(), variant="soft"),
        width="100%",
        align="center",
    )


def compute_page():
    return rx.vstack(
        rx.hstack(
            section_title(
                "Inference Fabric",
                "Compute",
                (
                    "Live routing status across MI BOND inference "
                    "and execution providers."
                ),
            ),
            rx.spacer(),
            rx.button(
                rx.icon("refresh-cw", size=15),
                "Refresh Providers",
                on_click=State.refresh_providers,
                variant="soft",
            ),
            width="100%",
            align="start",
        ),

        rx.grid(
            metric(
                "Agent Status",
                State.worker_status,
                State.provider_summary,
                "activity",
            ),
            metric(
                "Active Model",
                State.active_model,
                "Last successful mission",
                "brain",
            ),
            metric(
                "Runtime",
                State.active_runtime,
                "Current runtime",
                "server",
            ),
            metric(
                "Compute",
                State.active_compute,
                "Current compute route",
                "cpu",
            ),
            columns="4",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    status_dot("online"),
                    rx.vstack(
                        rx.text(
                            "Kaggle GPU Worker",
                            weight="bold",
                        ),
                        rx.text(
                            "Qwen2.5-1.5B · vLLM · NVIDIA T4",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.text(
                        (
                            "Primary free inference route. "
                            "Health is checked before Auto routing."
                        ),
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    width="100%",
                    align="center",
                ),

                rx.divider(),

                rx.hstack(
                    status_dot("standby"),
                    rx.vstack(
                        rx.text(
                            "OpenAI",
                            weight="bold",
                        ),
                        rx.text(
                            "Provider API fallback",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.text(
                        "Enabled when OPENAI_API_KEY exists.",
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    width="100%",
                ),

                rx.divider(),

                rx.hstack(
                    status_dot("standby"),
                    rx.vstack(
                        rx.text(
                            "Anthropic Claude",
                            weight="bold",
                        ),
                        rx.text(
                            "Provider API fallback",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.text(
                        "Enabled when ANTHROPIC_API_KEY exists.",
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    width="100%",
                ),

                rx.divider(),

                rx.hstack(
                    status_dot("standby"),
                    rx.vstack(
                        rx.text(
                            "xAI Grok",
                            weight="bold",
                        ),
                        rx.text(
                            "Provider API fallback",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.text(
                        "Enabled when XAI_API_KEY exists.",
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    width="100%",
                ),

                rx.divider(),

                rx.hstack(
                    status_dot("standby"),
                    rx.vstack(
                        rx.text(
                            "Mac Local",
                            weight="bold",
                        ),
                        rx.text(
                            "Ollama / local inference",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.text(
                        (
                            "Requires a secure reachable "
                            "OLLAMA_BASE_URL from Reflex Cloud."
                        ),
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    width="100%",
                ),

                spacing="4",
                align="stretch",
                width="100%",
            ),
            padding="24px",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("route", size=18),
                    rx.text(
                        "AUTO ROUTING ORDER",
                        weight="bold",
                    ),
                ),
                rx.divider(),
                rx.text(
                    (
                        "1. Kaggle / Qwen / vLLM  →  "
                        "2. OpenAI  →  "
                        "3. Claude  →  "
                        "4. Grok  →  "
                        "5. Local Ollama"
                    ),
                    size="2",
                ),
                rx.text(
                    (
                        "Explicit model selection overrides Auto. "
                        "If an explicitly selected provider is "
                        "unavailable, MI BOND reports the error "
                        "instead of silently pretending it executed."
                    ),
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="22px",
        ),

        width="100%",
        max_width="1500px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


def compute_card(name, role, accelerator, status, description):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(name, weight="bold", size="4"),
                    rx.text(
                        role.upper(),
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(status, variant="soft"),
                width="100%",
            ),
            rx.divider(),
            rx.text(accelerator, weight="medium", size="2"),
            rx.text(
                description,
                size="1",
                color=rx.color("gray", 10),
            ),
            rx.hstack(
                rx.text("CPU", size="1"),
                rx.text("GPU", size="1"),
                rx.text("RAM", size="1"),
                rx.text("VRAM", size="1"),
                spacing="3",
                color=rx.color("gray", 10),
            ),
            spacing="3",
            align="start",
            min_height="180px",
        ),
    )


# ============================================================
# SETTINGS
# ============================================================


def settings_page():
    return rx.vstack(
        section_title(
            "Configuration",
            "Settings",
            "Configure Bond's intelligence, execution runtime, routing and safety.",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("brain", size=19),
                    rx.heading("Models & Inference", size="4"),
                ),

                rx.grid(
                    setting_select(
                        "Provider",
                        State.selected_provider,
                        [
                            "Auto",
                            "Open Source",
                            "OpenAI",
                            "Anthropic",
                            "xAI",
                            "Hugging Face",
                            "Local",
                        ],
                        State.set_selected_provider,
                        "Source of model intelligence.",
                    ),

                    setting_select(
                        "Model",
                        State.selected_model,
                        [
                            "Auto",
                            "Qwen2.5-1.5B-Instruct",
                            "Qwen2.5-3B-Instruct",
                            "Qwen3-4B",
                            "Llama-3.2-3B-Instruct",
                            "OpenClaw Gateway",
                            "OpenAI API",
                            "Claude API",
                            "Grok API",
                            "Local Ollama",
                        ],
                        State.set_selected_model,
                        "Model family used by the agent.",
                    ),

                    setting_select(
                        "Runtime / Serving",
                        State.selected_runtime,
                        [
                            "Auto",
                            "Transformers",
                            "vLLM",
                            "MLX",
                            "Ollama",
                            "OpenClaw",
                            "Provider API",
                        ],
                        State.set_selected_runtime,
                        "How the selected model is served.",
                    ),

                    columns="3",
                    spacing="4",
                    width="100%",
                ),

                rx.grid(
                    setting_select(
                        "Max Tokens",
                        State.max_tokens,
                        [
                            "1024",
                            "2048",
                            "4096",
                            "8192",
                            "16384",
                            "32768",
                        ],
                        State.set_max_tokens,
                    ),

                    setting_select(
                        "Temperature",
                        State.temperature,
                        [
                            "0.0",
                            "0.2",
                            "0.4",
                            "0.7",
                            "1.0",
                        ],
                        State.set_temperature,
                    ),

                    setting_select(
                        "Compute",
                        State.selected_compute,
                        [
                            "Auto",
                            "Reflex CPU",
                            "Mac Apple Silicon",
                            "Kaggle T4 x2",
                            "Lightning GPU",
                            "NVIDIA CUDA Lab",
                            "AMD ROCm Lab",
                        ],
                        State.set_selected_compute,
                    ),

                    columns="3",
                    spacing="4",
                    width="100%",
                ),

                spacing="5",
                width="100%",
            ),
            padding="24px",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("route", size=19),
                    rx.heading("Routing & Failover", size="4"),
                ),

                setting_select(
                    "Routing Policy",
                    State.routing_policy,
                    [
                        "Balanced",
                        "GPU First",
                        "Fastest",
                        "Lowest Cost",
                        "Local Only",
                        "Best Quality",
                    ],
                    State.set_routing_policy,
                    "Bond can automatically fail over between available model and compute providers.",
                ),

                rx.text(
                    "Planned fallback chain",
                    weight="medium",
                    size="2",
                ),

                rx.code(
                    "Kaggle GPU → Mac Local → Lightning GPU → Provider API",
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),
            padding="24px",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("shield-check", size=19),
                    rx.heading("Safety & Permissions", size="4"),
                ),

                setting_select(
                    "Approval Policy",
                    State.approval_mode,
                    [
                        "Recommended",
                        "Strict",
                        "Manual Only",
                    ],
                    State.set_approval_mode,
                    "Controls which actions require your approval before execution.",
                ),

                rx.hstack(
                    rx.vstack(
                        rx.text("Long-term Memory", weight="medium"),
                        rx.text(
                            "Allow Bond to retain approved operational context.",
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.switch(
                        checked=State.memory_enabled,
                        on_change=State.toggle_memory,
                    ),
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),
            padding="24px",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# AGENTS
# ============================================================


def agent_card(name, role, description, status):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("bot", size=20),
                    padding="9px",
                    border_radius="10px",
                    background=rx.color("gray", 3),
                ),
                rx.vstack(
                    rx.text(name, weight="bold", size="3"),
                    rx.text(
                        role,
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(status, variant="soft"),
                width="100%",
            ),
            rx.text(
                description,
                size="2",
                color=rx.color("gray", 10),
            ),
            rx.divider(),
            rx.hstack(
                rx.text("Memory", size="1"),
                rx.text("Tools", size="1"),
                rx.text("Policies", size="1"),
                rx.spacer(),
                rx.button("Configure", size="1", variant="soft"),
                width="100%",
            ),
            spacing="3",
            align="start",
        ),
    )


def agent_card(name, role, model, tools, status="READY"):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("bot", size=20),
                rx.vstack(
                    rx.text(name, weight="bold", size="3"),
                    rx.text(
                        role,
                        size="1",
                        color=rx.color("gray", 10),
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(status, variant="soft"),
                width="100%",
                align="center",
            ),

            rx.divider(),

            rx.text(
                "Default model",
                size="1",
                color=rx.color("gray", 10),
            ),
            rx.text(model, weight="medium", size="2"),

            rx.text(
                "Capabilities",
                size="1",
                color=rx.color("gray", 10),
            ),
            rx.text(
                tools,
                size="2",
                color=rx.color("gray", 11),
            ),

            rx.button(
                "Use Agent",
                variant="soft",
                size="2",
                on_click=[
                    State.set_selected_agent(name),
                    State.set_page("Command Center"),
                ],
            ),

            spacing="3",
            align="start",
            width="100%",
        ),
        padding="20px",
        width="100%",
    )


def agents_page():
    return rx.vstack(
        rx.hstack(
            section_title(
                "Agent Runtime",
                "Agents",
                (
                    "Select the intelligence profile Agent 007 "
                    "uses for each mission."
                ),
            ),
            rx.spacer(),
            rx.button(
                rx.icon("refresh-cw", size=15),
                "Check Providers",
                on_click=State.refresh_providers,
                variant="soft",
            ),
            width="100%",
            align="start",
        ),

        rx.grid(
            metric(
                "Selected Agent",
                State.selected_agent,
                "Current mission persona",
                "bot",
            ),
            metric(
                "Model",
                State.active_model,
                "Last successful route",
                "brain",
            ),
            metric(
                "Compute",
                State.active_compute,
                "Last successful compute",
                "cpu",
            ),
            metric(
                "Providers",
                State.worker_status,
                State.provider_summary,
                "network",
            ),
            columns="4",
            spacing="3",
            width="100%",
        ),

        rx.grid(
            agent_card(
                "Bond",
                "Primary orchestration agent",
                "Auto",
                (
                    "Reasoning · planning · routing · "
                    "execution control"
                ),
            ),
            agent_card(
                "Research",
                "Research and synthesis",
                "Auto",
                (
                    "Investigation · synthesis · evidence · "
                    "briefings"
                ),
            ),
            agent_card(
                "Executive",
                "Decision and leadership analysis",
                "Auto",
                (
                    "Executive briefs · options · risk · "
                    "recommendations"
                ),
            ),
            agent_card(
                "Engineering",
                "Systems and AI infrastructure",
                "Auto",
                (
                    "Architecture · debugging · CUDA · ROCm · "
                    "cloud · networking"
                ),
            ),
            agent_card(
                "Communications",
                "Executive communications",
                "Auto",
                (
                    "Email · posts · summaries · stakeholder "
                    "communications"
                ),
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("shield-check", size=18),
                    rx.text(
                        "AGENT EXECUTION POLICY",
                        weight="bold",
                    ),
                ),
                rx.divider(),
                rx.text(
                    (
                        "Agents may reason and prepare work directly. "
                        "External writes, sends, publishing and "
                        "destructive actions will use the Approval "
                        "layer when those tools are connected."
                    ),
                    size="2",
                    color=rx.color("gray", 10),
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="22px",
        ),

        width="100%",
        max_width="1500px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# CONNECTIONS
# ============================================================


def connection_card(name, description, status, icon):
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=20),
                padding="10px",
                border_radius="10px",
                background=rx.color("gray", 3),
            ),
            rx.vstack(
                rx.text(name, weight="bold"),
                rx.text(
                    description,
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.vstack(
                rx.badge(status, variant="soft"),
                rx.button(
                    "Configure",
                    size="1",
                    variant="outline",
                ),
                align="end",
            ),
            width="100%",
            align="center",
        ),
    )


def connections_page():
    return rx.vstack(
        section_title(
            "Integrations",
            "Connections",
            "OAuth, APIs and MCP connections used by Agent 007.",
        ),

        rx.grid(
            connection_card(
                "Google",
                "Gmail · Calendar · Drive",
                "NOT CONNECTED",
                "mail",
            ),
            connection_card(
                "Microsoft",
                "Outlook · Calendar · OneDrive",
                "NOT CONNECTED",
                "mail",
            ),
            connection_card(
                "GitHub",
                "Repositories · Issues · Actions",
                "NOT CONNECTED",
                "folder-git-2",
            ),
            connection_card(
                "LinkedIn",
                "Approved publishing workflows",
                "NOT CONNECTED",
                "briefcase-business",
            ),
            connection_card(
                "Slack",
                "Channels · Messaging · Alerts",
                "NOT CONNECTED",
                "message-square",
            ),
            connection_card(
                "MCP",
                "External tool servers",
                "READY",
                "plug",
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# AUTOMATIONS
# ============================================================


def automation_row(name, trigger, action, status):
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon("workflow", size=18),
                padding="9px",
                border_radius="10px",
                background=rx.color("gray", 3),
            ),
            rx.vstack(
                rx.text(name, weight="bold"),
                rx.text(
                    trigger,
                    size="1",
                    color=rx.color("gray", 10),
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.text(action, size="2"),
            rx.badge(status, variant="soft"),
            width="100%",
            align="center",
        ),
    )


def automations_page():
    return rx.vstack(
        section_title(
            "Operations",
            "Automations",
            "Scheduled and condition-driven jobs that continue without an open chat.",
        ),

        rx.hstack(
            rx.button(
                rx.icon("plus", size=16),
                "New Automation",
            ),
            rx.button(
                rx.icon("workflow", size=16),
                "Workflow Builder",
                variant="outline",
            ),
        ),

        automation_row(
            "Morning Intelligence Brief",
            "Every weekday · 06:30",
            "Research → Summarize → Deliver",
            "PLANNED",
        ),
        automation_row(
            "GPU Health Watch",
            "Every hour",
            "Check workers → Alert on failure",
            "PLANNED",
        ),
        automation_row(
            "Important Email Watch",
            "On qualifying message",
            "Classify → Summarize → Notify",
            "PLANNED",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="4",
        align="stretch",
    )


# ============================================================
# SIMPLE PLACEHOLDERS
# ============================================================


def simple_page(title: str, subtitle: str, icon: str):
    return rx.vstack(
        section_title(
            "MI BOND",
            title,
            subtitle,
        ),
        rx.card(
            rx.vstack(
                rx.icon(icon, size=32),
                rx.heading(f"{title} workspace", size="4"),
                rx.text(
                    "This module is ready for the next implementation phase.",
                    color=rx.color("gray", 10),
                ),
                spacing="3",
                padding="40px",
                align="center",
            ),
            width="100%",
        ),
        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )



def workspace_metric(title, value, detail, icon):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=16),
                rx.text(
                    title.upper(),
                    size="1",
                    color=rx.color("gray", 10),
                ),
            ),
            rx.text(
                value,
                size="5",
                weight="bold",
            ),
            rx.text(
                detail,
                size="1",
                color=rx.color("gray", 10),
            ),
            spacing="2",
            align="start",
        ),
        flex="1",
    )


def chats_page():
    return rx.vstack(
        section_title(
            "Sessions",
            "Chats",
            "Persistent conversations and resumable Agent 007 missions.",
        ),

        rx.hstack(
            rx.button(
                rx.icon("plus", size=16),
                "New Chat",
            ),
            rx.input(
                placeholder="Search conversations...",
                max_width="420px",
            ),
            spacing="3",
        ),

        rx.grid(
            workspace_metric(
                "Active",
                "1",
                "Current command session",
                "messages-square",
            ),
            workspace_metric(
                "Saved",
                "0",
                "Persistent history layer",
                "archive",
            ),
            workspace_metric(
                "Model",
                State.active_model,
                "Current route",
                "brain",
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.image(
                        src="/mi-bond-favicon.svg",
                        width="28px",
                    ),
                    rx.vstack(
                        rx.text(
                            "MI Command Center",
                            weight="bold",
                        ),
                        rx.text(
                            State.execution_status,
                            size="1",
                            color=rx.color("gray", 10),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.badge(
                        "ACTIVE",
                        variant="soft",
                    ),
                    width="100%",
                ),

                rx.divider(),

                rx.text(
                    "Conversation persistence, titles, search, "
                    "branching and archival will use the future "
                    "MI BOND storage layer.",
                    color=rx.color("gray", 10),
                    size="2",
                ),

                spacing="3",
                align="start",
                width="100%",
            ),
            padding="22px",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


def tasks_page():
    return rx.vstack(
        section_title(
            "Mission Queue",
            "Tasks",
            "Track objectives from intake through execution and completion.",
        ),

        rx.grid(
            workspace_metric(
                "Queued",
                "0",
                "Waiting",
                "clock",
            ),
            workspace_metric(
                "Running",
                "0",
                "In execution",
                "activity",
            ),
            workspace_metric(
                "Completed",
                State.mission_count,
                "Session missions",
                "circle-check",
            ),
            workspace_metric(
                "Failed",
                "0",
                "Needs attention",
                "triangle-alert",
            ),
            columns="4",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "list-checks",
                        size=18,
                    ),
                    rx.text(
                        "MISSION QUEUE",
                        weight="bold",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("plus", size=15),
                        "New Task",
                        size="2",
                    ),
                    width="100%",
                ),

                rx.divider(),

                rx.cond(
                    State.last_command != "",
                    rx.hstack(
                        status_dot("online"),
                        rx.vstack(
                            rx.text(
                                State.last_command,
                                weight="medium",
                            ),
                            rx.text(
                                State.execution_status,
                                size="1",
                                color=rx.color("gray", 10),
                            ),
                            spacing="0",
                            align="start",
                        ),
                        rx.spacer(),
                        rx.badge(
                            "LATEST",
                            variant="soft",
                        ),
                        width="100%",
                    ),
                    rx.text(
                        "No missions have been submitted yet.",
                        color=rx.color("gray", 10),
                    ),
                ),

                spacing="3",
                align="start",
                width="100%",
            ),
            padding="22px",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


def approvals_page():
    return rx.vstack(
        section_title(
            "Human Control",
            "Approvals",
            "Review sensitive external actions before execution.",
        ),

        rx.grid(
            workspace_metric(
                "Waiting",
                State.approval_count,
                "Pending review",
                "shield-check",
            ),
            workspace_metric(
                "Policy",
                State.approval_mode,
                "Current safety mode",
                "lock-keyhole",
            ),
            workspace_metric(
                "Protected",
                "External",
                "Send · modify · publish · delete",
                "shield",
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "shield-check",
                        size=20,
                    ),
                    rx.text(
                        "APPROVAL QUEUE",
                        weight="bold",
                    ),
                ),

                rx.divider(),

                rx.text(
                    "No actions are waiting for approval.",
                    size="3",
                    weight="medium",
                ),

                rx.text(
                    "Email sends, repository writes, publishing, "
                    "destructive operations and other sensitive "
                    "actions will stop here before execution.",
                    size="2",
                    color=rx.color("gray", 10),
                ),

                spacing="3",
                align="start",
                width="100%",
            ),
            padding="24px",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


def memory_page():
    return rx.vstack(
        section_title(
            "Operational Context",
            "Memory",
            "Control what Agent 007 can retain and retrieve.",
        ),

        rx.grid(
            workspace_metric(
                "Session",
                "ACTIVE",
                "Current mission context",
                "messages-square",
            ),
            workspace_metric(
                "Long-term",
                "ENABLED",
                "Approved context only",
                "brain",
            ),
            workspace_metric(
                "Projects",
                "0",
                "Memory namespaces",
                "folder",
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "brain",
                        size=20,
                    ),
                    rx.text(
                        "MEMORY CONTROL",
                        weight="bold",
                    ),
                ),

                rx.divider(),

                rx.text(
                    "Memory stays independent from model providers. "
                    "Agent 007 will select the context supplied to "
                    "each model or worker.",
                    size="2",
                ),

                rx.text(
                    "Next layer: persistence, namespaces, retrieval, "
                    "retention controls and explicit forget operations.",
                    size="2",
                    color=rx.color("gray", 10),
                ),

                spacing="3",
                align="start",
                width="100%",
            ),
            padding="24px",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


def activity_page():
    return rx.vstack(
        section_title(
            "Audit & Observability",
            "Activity",
            "Inspect missions, routing, workers and future tool activity.",
        ),

        rx.grid(
            workspace_metric(
                "Missions",
                State.mission_count,
                "Current session",
                "crosshair",
            ),
            workspace_metric(
                "Worker",
                State.worker_status,
                "Kaggle inference",
                "cpu",
            ),
            workspace_metric(
                "Model",
                State.active_model,
                "Active intelligence",
                "brain",
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),

        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "activity",
                        size=20,
                    ),
                    rx.text(
                        "LATEST ACTIVITY",
                        weight="bold",
                    ),
                ),

                rx.divider(),

                rx.hstack(
                    status_dot("online"),
                    rx.vstack(
                        rx.text(
                            State.execution_status,
                            weight="medium",
                        ),
                        rx.cond(
                            State.last_command != "",
                            rx.text(
                                State.last_command,
                                size="1",
                                color=rx.color("gray", 10),
                            ),
                        ),
                        spacing="0",
                        align="start",
                    ),
                    width="100%",
                ),

                rx.text(
                    "Future audit records will include timestamps, "
                    "latency, tokens, cost, retries, tool calls, "
                    "approvals and artifacts.",
                    size="1",
                    color=rx.color("gray", 10),
                ),

                spacing="3",
                align="start",
                width="100%",
            ),
            padding="24px",
        ),

        width="100%",
        max_width="1450px",
        padding="34px 40px",
        spacing="5",
        align="stretch",
    )


# ============================================================
# PAGE ROUTER
# ============================================================


def routed_page():
    return rx.match(
        State.page,
        ("Command Center", command_center()),
        ("Chats", chats_page()),
        ("Agents", agents_page()),
        ("Tasks", tasks_page()),
        ("Automations", automations_page()),
        ("Approvals", approvals_page()),
        ("Memory", memory_page()),
        ("Connections", connections_page()),
        ("Compute", compute_page()),
        ("Activity", activity_page()),
        ("Settings", settings_page()),
        command_center(),
    )


def login_page():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "MI BOND",
                        font_size="28px",
                        weight="bold",
                        color="#e2b653",
                    ),
                    rx.text(
                        "AGENT 007",
                        font_size="11px",
                        letter_spacing=".34em",
                        color="#dce7f2",
                    ),
                    spacing="0",
                    align="start",
                ),

                rx.spacer(),

                rx.vstack(
                    rx.text(
                        "GLOBAL COMMAND NETWORK",
                        font_size="9px",
                        letter_spacing=".24em",
                        color="#bad0e6",
                    ),
                    rx.text(
                        "SECURE · PRIVATE · OPERATIONAL",
                        font_size="8px",
                        letter_spacing=".20em",
                        color="#708aa5",
                    ),
                    spacing="1",
                    align="end",
                ),

                width="100%",
                padding="26px 40px 0",
            ),

            rx.center(
                rx.card(
                    rx.vstack(
                        rx.image(
                            src="/mi-bond-favicon.svg",
                            width="108px",
                            height="108px",
                        ),

                        rx.text(
                            "MI BOND · AGENT 007",
                            font_size="10px",
                            letter_spacing=".25em",
                            color="#e2b653",
                            weight="bold",
                        ),

                        rx.heading(
                            "Secure Command Center",
                            size="7",
                            color="white",
                            text_align="center",
                        ),

                        rx.text(
                            "PLAN  |  REASON  |  EXECUTE",
                            font_size="10px",
                            letter_spacing=".28em",
                            color="#d4aa4d",
                        ),

                        rx.vstack(
                            rx.text("Username", size="1", color="white"),
                            rx.input(
                                value=State.username,
                                on_change=State.set_username,
                                width="100%",
                                background="rgba(3,7,12,.90)",
                                border_color="rgba(218,176,70,.5)",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),

                        rx.vstack(
                            rx.text("Password", size="1", color="white"),
                            rx.input(
                                value=State.password,
                                on_change=State.set_password,
                                type="password",
                                width="100%",
                                background="rgba(3,7,12,.90)",
                                border_color="rgba(39,145,229,.65)",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),

                        rx.cond(
                            State.login_error != "",
                            rx.text(
                                State.login_error,
                                color=rx.color("red", 10),
                                size="1",
                            ),
                        ),

                        rx.button(
                            "Access MI BOND",
                            on_click=State.login,
                            width="100%",
                            height="48px",
                            background=(
                                "linear-gradient(90deg,"
                                "#f3d174 0%,"
                                "#c99932 55%,"
                                "#2498ed 100%)"
                            ),
                            color="#030507",
                            weight="bold",
                            font_size="15px",
                        ),

                        rx.hstack(
                            rx.checkbox(
                                checked=State.remember_device,
                                on_change=State.set_remember_device,
                            ),
                            rx.text(
                                "Remember this trusted device",
                                size="1",
                                color="#9ba8b5",
                            ),
                            spacing="2",
                            width="100%",
                        ),

                        rx.text(
                            "PRIVATE · CONFIDENTIAL · AUTHORIZED ACCESS ONLY",
                            font_size="8px",
                            letter_spacing=".14em",
                            color="#718092",
                            text_align="center",
                        ),

                        spacing="4",
                        width="100%",
                        align="center",
                    ),

                    width="520px",
                    padding="34px",

                    background="rgba(4,9,15,.83)",
                    border="1px solid rgba(220,177,70,.38)",
                    box_shadow=(
                        "0 35px 100px rgba(0,0,0,.68),"
                        "0 0 60px rgba(30,135,220,.10)"
                    ),
                    backdrop_filter="blur(18px)",
                ),

                flex="1",
                width="100%",
            ),

            rx.hstack(
                rx.vstack(
                    rx.text(
                        "WORLDWIDE INTELLIGENCE GRID",
                        font_size="9px",
                        letter_spacing=".22em",
                        color="#a9bfd4",
                    ),
                    rx.text(
                        "AGENTS · MODELS · TOOLS · COMPUTE",
                        font_size="8px",
                        letter_spacing=".17em",
                        color="#6e8aa5",
                    ),
                    spacing="1",
                    align="start",
                ),

                rx.spacer(),

                rx.vstack(
                    rx.text(
                        '"SAME MISSION.',
                        font_size="13px",
                        color="#d9b359",
                    ),
                    rx.text(
                        'A SMARTER WORLD."',
                        font_size="13px",
                        color="#d9b359",
                    ),
                    rx.text(
                        "— 007",
                        font_size="11px",
                        color="#aab4bf",
                    ),
                    spacing="0",
                    align="end",
                ),

                width="100%",
                padding="0 40px 26px",
            ),

            width="100%",
            min_height="100vh",
            justify="between",
        ),

        width="100%",
        min_height="100vh",

        background_image=(
            "linear-gradient(rgba(0,0,0,.05),rgba(0,0,0,.25)),"
            "url('/mi-bond-world.svg')"
        ),
        background_size="cover",
        background_position="center",
        background_repeat="no-repeat",
    )


def dashboard_shell():
    return rx.hstack(
        sidebar(),
        page_shell(routed_page()),
        width="100%",
        min_height="100vh",
        spacing="0",
        align="start",
    )


def index():
    return rx.cond(
        State.authenticated,
        dashboard_shell(),
        login_page(),
    )


app = rx.App(
    head_components=[
        rx.el.link(
            rel="icon",
            href="/mi-bond-favicon.svg",
            type="image/svg+xml",
        )
    ]
)

app.add_page(
    index,
    title="MI BOND · Agent 007",
    description="MI BOND Agentic AI Command Center",
    image="/mi-bond-favicon.svg",
)
