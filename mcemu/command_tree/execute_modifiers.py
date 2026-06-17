from typing import List

from ..commands.data import set_nested_dict
from ..context import ExecutionContext
from .arguments import TargetSelectorData


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


import math
from ..entity import Entity


class ExecutePositionedModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        pos = args.get("pos")
        if pos:
            new_ctx = ctx.clone()
            new_ctx.position = (
                pos[0].resolve(ctx.position[0]),
                pos[1].resolve(ctx.position[1]),
                pos[2].resolve(ctx.position[2])
            )
            return [new_ctx]
        return [ctx]


class ExecutePositionedAsModifier(ExecuteModifier):
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


class ExecuteFacingModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        pos = args.get("pos")
        if pos:
            target_x = pos[0].resolve(ctx.position[0])
            target_y = pos[1].resolve(ctx.position[1])
            target_z = pos[2].resolve(ctx.position[2])

            dx = target_x - ctx.position[0]
            dy = target_y - ctx.position[1]
            dz = target_z - ctx.position[2]

            yaw = math.degrees(math.atan2(-dx, dz))
            pitch = math.degrees(-math.atan2(dy, math.sqrt(dx * dx + dz * dz)))

            new_ctx = ctx.clone()
            new_ctx.rotation = (yaw, pitch)
            return [new_ctx]
        return [ctx]


class ExecuteFacingEntityModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        targets = args.get("target", [])
        contexts = []
        for t in targets:
            entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
            if entity:
                dx = entity.pos[0] - ctx.position[0]
                dy = entity.pos[1] - ctx.position[1]
                dz = entity.pos[2] - ctx.position[2]
                yaw = math.degrees(math.atan2(-dx, dz))
                pitch = math.degrees(-math.atan2(dy, math.sqrt(dx * dx + dz * dz)))

                new_ctx = ctx.clone()
                new_ctx.rotation = (yaw, pitch)
                contexts.append(new_ctx)
        return contexts


class ExecuteRotatedModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        yaw_arg = args.get("yaw")
        pitch_arg = args.get("pitch")
        if yaw_arg and pitch_arg:
            new_ctx = ctx.clone()
            new_ctx.rotation = (
                yaw_arg.resolve(ctx.rotation[0]),
                pitch_arg.resolve(ctx.rotation[1])
            )
            return [new_ctx]
        return [ctx]


class ExecuteRotatedAsModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        targets = args.get("target", [])
        contexts = []
        for t in targets:
            entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
            if entity:
                new_ctx = ctx.clone()
                new_ctx.rotation = entity.rotation
                contexts.append(new_ctx)
        return contexts


class ExecuteAlignedModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        axes = args.get("axes", "")
        new_ctx = ctx.clone()
        x, y, z = list(ctx.position)
        if "x" in axes: x = math.floor(x)
        if "y" in axes: y = math.floor(y)
        if "z" in axes: z = math.floor(z)
        new_ctx.position = (x, y, z)
        return [new_ctx]


class ExecuteAnchoredModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        anchor = args.get("anchor", "feet")
        new_ctx = ctx.clone()
        new_ctx.anchor = anchor
        return [new_ctx]


class ExecuteInModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        dimension = args.get("dimension", "minecraft:overworld")
        new_ctx = ctx.clone()
        new_ctx.dimension = dimension
        return [new_ctx]


class ExecuteOnModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        relation = args.get("relation", "")
        if not ctx.executor: return []

        contexts = []
        if relation == "owner":
            owner_uuid = ctx.executor.nbt.get("Owner")
            if owner_uuid:
                owner = next((e for e in ctx.world.entities if str(e.uuid) == str(owner_uuid)), None)
                if owner:
                    new_ctx = ctx.clone()
                    new_ctx.executor = owner
                    contexts.append(new_ctx)
        elif relation == "vehicle":
            vehicle_uuid = ctx.executor.nbt.get("Vehicle")
            if vehicle_uuid:
                vehicle = next((e for e in ctx.world.entities if str(e.uuid) == str(vehicle_uuid)), None)
                if vehicle:
                    new_ctx = ctx.clone()
                    new_ctx.executor = vehicle
                    contexts.append(new_ctx)
        elif relation == "passengers":
            passengers = ctx.executor.nbt.get("Passengers", [])
            for p_uuid in passengers:
                passenger = next((e for e in ctx.world.entities if str(e.uuid) == str(p_uuid)), None)
                if passenger:
                    new_ctx = ctx.clone()
                    new_ctx.executor = passenger
                    contexts.append(new_ctx)
        elif relation == "attacker" or relation == "target":
            target_uuid = ctx.executor.nbt.get("Target")
            if target_uuid:
                target = next((e for e in ctx.world.entities if str(e.uuid) == str(target_uuid)), None)
                if target:
                    new_ctx = ctx.clone()
                    new_ctx.executor = target
                    contexts.append(new_ctx)
        elif relation == "origin":
            origin_uuid = ctx.executor.nbt.get("Origin")
            if origin_uuid:
                origin = next((e for e in ctx.world.entities if str(e.uuid) == str(origin_uuid)), None)
                if origin:
                    new_ctx = ctx.clone()
                    new_ctx.executor = origin
                    contexts.append(new_ctx)
        return contexts


class ExecuteSummonModifier(ExecuteModifier):
    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        entity_type = args.get("entity_type", "minecraft:pig")
        if ":" not in entity_type:
            entity_type = f"minecraft:{entity_type}"
        new_entity = Entity(entity_type, pos=ctx.position)
        new_entity.rotation = ctx.rotation
        ctx.world.add_entity(new_entity)

        new_ctx = ctx.clone()
        new_ctx.executor = new_entity
        return [new_ctx]


class ExecuteIfScoreModifier(ExecuteModifier):
    def __init__(self, invert: bool = False):
        self.invert = invert

    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        target = args.get("target")
        target_obj = args.get("target_obj")
        op = args.get("op")
        source = args.get("source")
        source_obj = args.get("source_obj")
        
        if not target or not source:
            return [] if not self.invert else [ctx]

        target_str = target.base if isinstance(target, TargetSelectorData) else target[0] if target else ""
        source_str = source.base if isinstance(source, TargetSelectorData) else source[0] if source else ""

        try:
            val1 = ctx.world.get_score(target_str, target_obj)
            val2 = ctx.world.get_score(source_str, source_obj)
            
            if op == "<": condition = val1 < val2
            elif op == "<=": condition = val1 <= val2
            elif op == "=": condition = val1 == val2
            elif op == ">=": condition = val1 >= val2
            elif op == ">": condition = val1 > val2
            else: return [] if not self.invert else [ctx]
            
            if self.invert:
                condition = not condition
                
            return [ctx] if condition else []
        except Exception:
            return [] if not self.invert else [ctx]


class ExecuteIfScoreMatchesModifier(ExecuteModifier):
    def __init__(self, invert: bool):
        self.invert = invert

    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        target = args.get("target")
        target_obj = args.get("target_obj")
        range_val = args.get("range")
        
        if not target:
            return [] if not self.invert else [ctx]

        target_str = target.base if isinstance(target, TargetSelectorData) else target[0] if target else ""
        
        try:
            val = ctx.world.get_score(target_str, target_obj)
        except RuntimeError:
            return [] if not self.invert else [ctx]

        result = True
        range_min, range_max = range_val
        if range_min is not None and val < range_min: result = False
        if range_max is not None and val > range_max: result = False

        if self.invert:
            result = not result

        return [ctx] if result else []


class ExecuteIfEntityModifier(ExecuteModifier):
    def __init__(self, invert: bool = False):
        self.invert = invert

    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        targets = args.get("target", [])

        found = False
        for t in targets:
            entity = next((e for e in ctx.world.entities if e.uuid == t or e.name == t), None)
            if entity:
                found = True
                break

        if self.invert:
            found = not found

        return [ctx] if found else []


class ExecuteIfBlockModifier(ExecuteModifier):
    def __init__(self, invert: bool = False):
        self.invert = invert

    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        pos = args.get("pos")
        block_state = args.get("block")

        target_x = math.floor(pos[0].resolve(ctx.position[0]))
        target_y = math.floor(pos[1].resolve(ctx.position[1]))
        target_z = math.floor(pos[2].resolve(ctx.position[2]))

        current_block = ctx.world.blocks.get((target_x, target_y, target_z), "minecraft:air")

        result = (current_block == block_state.block_id)
        if self.invert:
            result = not result

        return [ctx] if result else []


class ExecuteIfBlocksModifier(ExecuteModifier):
    def __init__(self, invert: bool = False):
        self.invert = invert

    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        result = False
        if self.invert:
            result = not result
        return [ctx] if result else []


class ExecuteIfDataModifier(ExecuteModifier):
    def __init__(self, invert: bool = False):
        self.invert = invert

    def modify(self, ctx: ExecutionContext, args: dict) -> List[ExecutionContext]:
        result = False
        if self.invert:
            result = not result
        return [ctx] if result else []
