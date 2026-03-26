"""Sandbox creation form with validation.

Wizard-style form for creating new NemoClaw sandboxes.
"""

import streamlit as st
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import re

@dataclass
class SandboxConfig:
    name: str
    agent_type: str
    model: str
    workspace_path: str
    system_prompt: str = ""
    max_memory_gb: float = 8.0
    gpu_enabled: bool = True
    auto_start: bool = False

# Validation patterns
VALID_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')
VALID_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_./~\\-]+$')

AGENT_TYPES = [
    "openai",
    "anthropic",
    "ollama",
    "nvidia-nim",
    "custom"
]

MODELS_BY_AGENT = {
    "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    "ollama": ["llama2", "llama3", "mistral", "codellama"],
    "nvidia-nim": ["nemotron-4", "nemotron-3", "mixtral-8x7b"],
    "custom": ["custom-model"]
}

def validate_sandbox_name(name: str) -> tuple[bool, str]:
    """Validate sandbox name."""
    if not name:
        return False, "Name is required"
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    if len(name) > 64:
        return False, "Name must be at most 64 characters"
    if not VALID_NAME_PATTERN.match(name):
        return False, "Name must start with a letter and contain only letters, numbers, underscores, and hyphens"
    return True, ""

def validate_workspace_path(path: str) -> tuple[bool, str]:
    """Validate workspace path."""
    if not path:
        return False, "Workspace path is required"
    if not VALID_PATH_PATTERN.match(path):
        return False, "Path contains invalid characters"
    
    # Expand path and check if parent exists
    expanded = Path(path).expanduser()
    parent = expanded.parent
    
    if not parent.exists():
        return False, f"Parent directory does not exist: {parent}"
    
    # Check if path already exists
    if expanded.exists():
        return False, f"Path already exists: {path}"
    
    return True, ""

def validate_memory_gb(memory: float) -> tuple[bool, str]:
    """Validate memory allocation."""
    if memory < 1:
        return False, "Memory must be at least 1 GB"
    if memory > 128:
        return False, "Memory must be at most 128 GB"
    return True, ""

def render_sandbox_creation_wizard(openshell_service, on_create=None):
    """Render sandbox creation wizard form."""
    
    st.header("🆕 Create New Sandbox")
    st.caption("Configure a new NemoClaw sandbox")
    
    # Initialize form state
    if 'sandbox_form_step' not in st.session_state:
        st.session_state.sandbox_form_step = 1
    if 'form_errors' not in st.session_state:
        st.session_state.form_errors = {}
    if 'form_values' not in st.session_state:
        st.session_state.form_values = {}
    
    # Progress bar
    progress = (st.session_state.sandbox_form_step - 1) / 3
    st.progress(progress, text=f"Step {st.session_state.sandbox_form_step} of 4")
    
    # Form container
    with st.container():
        if st.session_state.sandbox_form_step == 1:
            _render_step_1_basic_info()
        elif st.session_state.sandbox_form_step == 2:
            _render_step_2_agent_config()
        elif st.session_state.sandbox_form_step == 3:
            _render_step_3_resources()
        elif st.session_state.sandbox_form_step == 4:
            _render_step_4_review(openshell_service, on_create)
    
    # Navigation buttons
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.sandbox_form_step > 1:
            if st.button("← Previous", use_container_width=True):
                st.session_state.sandbox_form_step -= 1
                st.rerun()
    
    with col3:
        if st.session_state.sandbox_form_step < 4:
            if st.button("Next →", type="primary", use_container_width=True):
                if _validate_current_step():
                    st.session_state.sandbox_form_step += 1
                    st.rerun()
    
    # Show validation errors
    if st.session_state.form_errors:
        with st.expander("❌ Validation Errors", expanded=True):
            for field, error in st.session_state.form_errors.items():
                st.error(f"**{field}:** {error}")

def _render_step_1_basic_info():
    """Render Step 1: Basic Information."""
    st.subheader("Step 1: Basic Information")
    
    # Sandbox name
    name = st.text_input(
        "Sandbox Name *",
        value=st.session_state.form_values.get('name', ''),
        placeholder="my-sandbox-1",
        help="Unique identifier for the sandbox. Must start with a letter, alphanumeric and hyphens only.",
        key="form_name"
    )
    st.session_state.form_values['name'] = name
    
    # Validation hint
    valid, msg = validate_sandbox_name(name)
    if not valid and name:
        st.warning(msg)
    elif valid and name:
        st.success("✓ Valid name")
    
    # Description (optional)
    description = st.text_area(
        "Description",
        value=st.session_state.form_values.get('description', ''),
        placeholder="What will this sandbox be used for?",
        key="form_description"
    )
    st.session_state.form_values['description'] = description
    
    # Workspace path
    workspace = st.text_input(
        "Workspace Path *",
        value=st.session_state.form_values.get('workspace', '~/.nemoclaw/workspaces/my-sandbox'),
        placeholder="~/.nemoclaw/workspaces/my-sandbox",
        help="Directory where sandbox files will be stored.",
        key="form_workspace"
    )
    st.session_state.form_values['workspace'] = workspace
    
    # Path validation hint
    valid, msg = validate_workspace_path(workspace)
    if not valid and workspace:
        st.warning(msg)
    elif valid and workspace:
        st.success("✓ Valid path")
    
    # Create directory toggle
    if st.checkbox("Create workspace directory if it doesn't exist", value=True, key="form_create_dir"):
        st.session_state.form_values['create_dir'] = True

def _render_step_2_agent_config():
    """Render Step 2: Agent Configuration."""
    st.subheader("Step 2: Agent Configuration")
    
    # Agent type
    agent_type = st.selectbox(
        "Agent Type *",
        options=AGENT_TYPES,
        index=AGENT_TYPES.index(st.session_state.form_values.get('agent_type', 'openai')),
        help="The AI agent framework to use.",
        key="form_agent_type"
    )
    st.session_state.form_values['agent_type'] = agent_type
    
    # Model selection based on agent type
    available_models = MODELS_BY_AGENT.get(agent_type, [])
    current_model = st.session_state.form_values.get('model', available_models[0] if available_models else '')
    
    model = st.selectbox(
        "Model *",
        options=available_models,
        index=available_models.index(current_model) if current_model in available_models else 0,
        help="The AI model to use.",
        key="form_model"
    )
    st.session_state.form_values['model'] = model
    
    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state.form_values.get('system_prompt', ''),
        placeholder="You are a helpful AI assistant...",
        help="The system prompt that defines the agent's behavior.",
        key="form_system_prompt"
    )
    st.session_state.form_values['system_prompt'] = system_prompt
    
    # Environment variables
    with st.expander("Environment Variables (Advanced)"):
        env_vars = st.text_area(
            "Additional Environment Variables",
            value=st.session_state.form_values.get('env_vars', ''),
            placeholder="KEY1=value1\nKEY2=value2",
            help="One variable per line in KEY=value format.",
            key="form_env_vars"
        )
        st.session_state.form_values['env_vars'] = env_vars

def _render_step_3_resources():
    """Render Step 3: Resource Configuration."""
    st.subheader("Step 3: Resource Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Memory allocation
        memory = st.slider(
            "Max Memory (GB) *",
            min_value=1,
            max_value=32,
            value=int(st.session_state.form_values.get('memory_gb', 8)),
            help="Maximum memory allocated to the sandbox.",
            key="form_memory"
        )
        st.session_state.form_values['memory_gb'] = memory
        
        # Memory validation
        valid, msg = validate_memory_gb(memory)
        if not valid:
            st.warning(msg)
    
    with col2:
        # GPU toggle
        gpu_enabled = st.toggle(
            "Enable GPU",
            value=st.session_state.form_values.get('gpu_enabled', True),
            help="Allow sandbox to access GPU resources.",
            key="form_gpu"
        )
        st.session_state.form_values['gpu_enabled'] = gpu_enabled
        
        if gpu_enabled:
            st.success("✓ GPU enabled")
        else:
            st.info("ℹ️ CPU-only mode")
    
    # Auto-start toggle
    auto_start = st.toggle(
        "Auto-start after creation",
        value=st.session_state.form_values.get('auto_start', False),
        help="Automatically start the sandbox after creation.",
        key="form_auto_start"
    )
    st.session_state.form_values['auto_start'] = auto_start
    
    # Resource preview
    st.divider()
    st.subheader("Resource Preview")
    
    total_memory = st.slider("Total System Memory (GB)", min_value=8, max_value=256, value=64, disabled=True)
    
    # Show memory allocation visualization
    memory_pct = (memory / total_memory) * 100
    st.progress(memory_pct / 100, text=f"{memory} GB allocated ({memory_pct:.1f}% of system)")
    
    if memory_pct > 50:
        st.warning("⚠️ High memory allocation. Ensure other sandboxes have sufficient resources.")

def _render_step_4_review(openshell_service, on_create):
    """Render Step 4: Review and Create."""
    st.subheader("Step 4: Review Configuration")
    
    # Collect all values
    config = SandboxConfig(
        name=st.session_state.form_values.get('name', ''),
        agent_type=st.session_state.form_values.get('agent_type', 'openai'),
        model=st.session_state.form_values.get('model', ''),
        workspace_path=st.session_state.form_values.get('workspace', ''),
        system_prompt=st.session_state.form_values.get('system_prompt', ''),
        max_memory_gb=st.session_state.form_values.get('memory_gb', 8),
        gpu_enabled=st.session_state.form_values.get('gpu_enabled', True),
        auto_start=st.session_state.form_values.get('auto_start', False)
    )
    
    # Display configuration summary
    with st.container():
        st.markdown("### Configuration Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            st.write(f"- **Name:** `{config.name}`")
            st.write(f"- **Workspace:** `{config.workspace_path}`")
            desc = st.session_state.form_values.get('description', '')
            if desc:
                st.write(f"- **Description:** {desc}")
        
        with col2:
            st.markdown("**Agent Configuration**")
            st.write(f"- **Agent Type:** {config.agent_type}")
            st.write(f"- **Model:** {config.model}")
            st.write(f"- **GPU Enabled:** {'Yes' if config.gpu_enabled else 'No'}")
            st.write(f"- **Auto-start:** {'Yes' if config.auto_start else 'No'}")
        
        st.markdown("**Resources**")
        st.write(f"- **Max Memory:** {config.max_memory_gb} GB")
    
    # Validation summary
    st.divider()
    
    errors = []
    
    valid, msg = validate_sandbox_name(config.name)
    if not valid:
        errors.append(f"Name: {msg}")
    
    valid, msg = validate_workspace_path(config.workspace_path)
    if not valid:
        errors.append(f"Workspace: {msg}")
    
    valid, msg = validate_memory_gb(config.max_memory_gb)
    if not valid:
        errors.append(f"Memory: {msg}")
    
    if errors:
        st.error("**Cannot create sandbox - please fix the following errors:**")
        for error in errors:
            st.write(f"- {error}")
    else:
        st.success("✓ All validations passed")
        
        # Create button
        if st.button("🚀 Create Sandbox", type="primary", use_container_width=True):
            with st.spinner("Creating sandbox..."):
                try:
                    # Create workspace directory if needed
                    if st.session_state.form_values.get('create_dir', True):
                        workspace_path = Path(config.workspace_path).expanduser()
                        workspace_path.mkdir(parents=True, exist_ok=True)
                    
                    # Build sandbox creation command
                    sandbox_config = {
                        'name': config.name,
                        'agent_type': config.agent_type,
                        'model': config.model,
                        'workspace_path': config.workspace_path,
                        'system_prompt': config.system_prompt,
                        'max_memory_gb': config.max_memory_gb,
                        'gpu_enabled': config.gpu_enabled,
                        'auto_start': config.auto_start
                    }
                    
                    # Call openshell service to create sandbox
                    result = openshell_service._execute(
                        "sandbox", "create", 
                        "--config", str(sandbox_config),
                        capture_json=True
                    )
                    
                    if result.get('success') or isinstance(result, dict):
                        st.success(f"✅ Sandbox '{config.name}' created successfully!")
                        
                        if config.auto_start:
                            st.info("🚀 Auto-starting sandbox...")
                            openshell_service.start_sandbox(config.name)
                        
                        if on_create:
                            on_create(config.name)
                        
                        # Reset form
                        st.session_state.sandbox_form_step = 1
                        st.session_state.form_values = {}
                        st.session_state.form_errors = {}
                        
                    else:
                        st.error(f"❌ Failed to create sandbox: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error creating sandbox: {e}")
                    import traceback
                    st.code(traceback.format_exc())

def _validate_current_step() -> bool:
    """Validate the current form step."""
    errors = {}
    step = st.session_state.sandbox_form_step
    values = st.session_state.form_values
    
    if step == 1:
        # Validate basic info
        name = values.get('name', '')
        valid, msg = validate_sandbox_name(name)
        if not valid:
            errors['Name'] = msg
        
        workspace = values.get('workspace', '')
        valid, msg = validate_workspace_path(workspace)
        if not valid:
            errors['Workspace'] = msg
    
    elif step == 2:
        # Validate agent config
        if not values.get('agent_type'):
            errors['Agent Type'] = "Required"
        if not values.get('model'):
            errors['Model'] = "Required"
    
    elif step == 3:
        # Validate resources
        memory = values.get('memory_gb', 0)
        valid, msg = validate_memory_gb(memory)
        if not valid:
            errors['Memory'] = msg
    
    st.session_state.form_errors = errors
    return len(errors) == 0

# Simple creation form for quick sandbox creation
def render_quick_sandbox_form(openshell_service, on_create=None):
    """Render a simplified quick creation form."""
    
    with st.expander("➕ Quick Create Sandbox", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Sandbox Name", placeholder="my-sandbox", key="quick_name")
        
        with col2:
            agent_type = st.selectbox(
                "Agent Type",
                options=AGENT_TYPES,
                index=0,
                key="quick_agent"
            )
        
        model = st.selectbox(
            "Model",
            options=MODELS_BY_AGENT.get(agent_type, []),
            index=0,
            key="quick_model"
        )
        
        workspace = st.text_input(
            "Workspace Path",
            value=f"~/.nemoclaw/workspaces/{name if name else 'new-sandbox'}",
            key="quick_workspace"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            gpu = st.checkbox("GPU", value=True, key="quick_gpu")
        with col2:
            memory = st.slider("Memory (GB)", 1, 32, 8, key="quick_memory")
        with col3:
            auto_start = st.checkbox("Auto-start", key="quick_auto")
        
        if st.button("Create", type="primary", use_container_width=True, key="quick_create_btn"):
            # Validate
            valid, msg = validate_sandbox_name(name)
            if not valid:
                st.error(f"Invalid name: {msg}")
                return
            
            valid, msg = validate_workspace_path(workspace)
            if not valid:
                st.error(f"Invalid workspace: {msg}")
                return
            
            with st.spinner("Creating..."):
                try:
                    # Create workspace
                    Path(workspace).expanduser().mkdir(parents=True, exist_ok=True)
                    
                    # Create sandbox
                    sandbox_config = {
                        'name': name,
                        'agent_type': agent_type,
                        'model': model,
                        'workspace_path': workspace,
                        'gpu_enabled': gpu,
                        'max_memory_gb': memory,
                        'auto_start': auto_start
                    }
                    
                    result = openshell_service._execute(
                        "sandbox", "create",
                        "--config", str(sandbox_config)
                    )
                    
                    st.success(f"Created '{name}'!")
                    if on_create:
                        on_create(name)
                        
                except Exception as e:
                    st.error(f"Error: {e}")
