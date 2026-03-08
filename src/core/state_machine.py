# src/core/state_machine.py

# 导入之前定义的状态模型
try:
    from .models import StateNode
except ImportError:
    from models import StateNode
# 导入命令注册中心
try:
    from .registry import CommandRegistry
except ImportError:
    from registry import CommandRegistry
# 导入配置常量
try:
    from .config import FREE_MODE_MAX_DEPTH
except ImportError:
    from config import FREE_MODE_MAX_DEPTH
# 导入 typing 模块
from typing import Optional, List, Dict


# 定义状态机类
class StateMachine:
    # 含义：初始化方法，需要传入命令注册中心实例
    def __init__(self, registry: CommandRegistry):
        # 含义：存储命令注册中心引用，用于获取命令
        self.registry = registry
        # 含义：创建一个字典，存储所有已注册的状态节点，Key 为状态 ID
        self._states: Dict[str, StateNode] = {}
        # 含义：记录当前所处的状态 ID，初始为 None
        self._current_state_id: Optional[str] = None

    # 含义：注册一个状态节点到状态机
    def register_state(self, state: StateNode) -> bool:
        # 含义：如果状态 ID 已存在，拒绝注册以防冲突
        if state.id in self._states:
            return False
        # 含义：将状态存入字典
        self._states[state.id] = state
        return True

    # 含义：获取当前状态对象
    def get_current_state(self) -> Optional[StateNode]:
        # 含义：如果当前没有状态，返回 None
        if not self._current_state_id:
            return None
        # 含义：从字典中返回当前状态对象
        return self._states.get(self._current_state_id)

    # 含义：计算某个状态节点的嵌套深度
    def calculate_depth(self, state_id: str) -> int:
        # 含义：初始化深度为 0
        depth = 0
        # 含义：获取当前状态对象
        current = self._states.get(state_id)
        # 含义：当状态存在且有父级时，循环向上追溯
        while current and current.parent_id:
            # 含义：深度加 1
            depth += 1
            # 含义：获取父级状态对象
            current = self._states.get(current.parent_id)
        # 含义：返回计算出的总深度
        return depth

    # 含义：切换到新状态的核心方法
    def transition_to(self, target_state_id: str) -> tuple[bool, str]:
        # 含义：检查目标状态是否存在
        if target_state_id not in self._states:
            # 含义：如果不存在，返回失败和错误信息
            return False, f"State {target_state_id} not found"

        # 含义：获取目标状态对象
        target_state = self._states[target_state_id]

        # 含义：计算目标状态的深度
        new_depth = self.calculate_depth(target_state_id)

        # 含义：如果目标状态是自由模式，检查深度限制
        if target_state.mode == "free" and new_depth > FREE_MODE_MAX_DEPTH:
            # 含义：如果超过 5 层，拒绝切换
            return False, f"Free mode depth limit exceeded ({new_depth} > {FREE_MODE_MAX_DEPTH})"

        # 含义：更新目标状态的深度记录（确保数据一致性）
        target_state.depth = new_depth

        # 含义：更新当前状态 ID 为目标 ID
        self._current_state_id = target_state_id

        # 含义：返回成功
        return True, "Transition successful"

    # 含义：获取当前状态可披露的命令列表
    def get_disclosed_commands(self) -> List:
        # 含义：获取当前状态对象
        current_state = self.get_current_state()
        # 含义：如果无当前状态，返回空列表
        if not current_state:
            return []

        # 含义：从注册中心获取状态允许的普通命令
        cmds = self.registry.get_disclosed_commands(current_state.available_command_ids)

        # 含义：获取系统逻辑命令（如返回上一级），通常全局可用
        sys_cmds = self.registry.get_system_commands()

        # 含义：合并普通命令和系统命令
        # 注意：这里简单合并，实际可根据逻辑命令的适用状态做过滤
        return cmds + sys_cmds

    # 含义：获取当前状态的父亲状态 ID（用于返回上一级逻辑）
    def get_parent_state_id(self) -> Optional[str]:
        # 含义：获取当前状态
        current = self.get_current_state()
        # 含义：如果存在且有父级，返回父级 ID
        if current:
            return current.parent_id
        # 含义：否则返回 None
        return None