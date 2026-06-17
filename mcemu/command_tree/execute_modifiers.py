from typing import List

from ..commands.data import set_nested_dict
from ..context import ExecutionContext


class ExecuteModifier:
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        raise NotImplementedError()

    def on_result(self, ctx: ExecutionContext, args: dict, result: int):
        pass


class ExecuteAsModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        targets = args.get("target", [])
        contexts = []
        for t in targets:
            entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
            if entity:
                new_ctx = ctx.clone()
                new_ctx.executor = entity
                contexts.append(new_ctx)
        return contexts


class ExecuteAtModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        targets = args.get("target", [])
        contexts = []
        for t in targets:
            entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
            if entity:
                new_ctx = ctx.clone()
                new_ctx.position = entity.pos
                contexts.append(new_ctx)
        return contexts


class ExecuteStoreScoreModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        return [ctx]

    def on_result(self, ctx: ExecutionContext, args: dict, result: int):
        targets = args.get("store_target", [])
        objective = args.get("store_objective", "")
        for t in targets:
            ctx.world.set_score(t, objective, int(result))


class ExecuteStoreResultModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        return [ctx]

    def on_result(self, ctx: ExecutionContext, args: dict, result: int):
        targets = args.get("store_target", [])
        store_type = args.get("store_type", "entity")
        path = args.get("store_path", "")
        multiplier = float(args.get("store_multiplier", 1.0))
        datatype = args.get("store_datatype", "int")

        if "NBTType" in store_type:
            store_type = store_type.split(".")[-1].lower()

        scaled_res = result * multiplier
        if "int" in datatype.lower():
            scaled_res = int(scaled_res)
        elif "byte" in datatype.lower():
            scaled_res = int(scaled_res) & 0xFF

        for t in targets:
            target_key = f"{store_type}:{t}"
            if target_key not in ctx.world.nbt_storage:
                ctx.world.nbt_storage[target_key] = {}
            set_nested_dict(ctx.world.nbt_storage[target_key], path, scaled_res)
