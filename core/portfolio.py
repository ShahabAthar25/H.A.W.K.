from typing import Dict, List, Union


class Instrument:
    def __init__(self, symbol: str, capital: float = 0.0):
        self.symbol = symbol
        self.capital = capital

    def __repr__(self):
        return f"<Instrument symbol='{self.symbol}' capital={self.capital}>"


class Group:
    def __init__(self, name: str, capital: float = 0.0):
        self.name = name
        self.members: List[Union['Group', Instrument]] = []
        self.capital = capital

    def add(self, member: Union['Group', Instrument]):
        self.members.append(member)

    def get_flat_allocations(self) -> Dict[str, float]:
        result = {}
        for member in self.members:
            if isinstance(member, Instrument):
                result[member.symbol] = member.capital
            elif isinstance(member, Group):
                result.update(member.get_flat_allocations())
        return result


    def __repr__(self):
        return f"<Group name='{self.name}' capital={self.capital} members={self.members}>"


class Portfolio:
    def __init__(self, balance: float, group_config: Dict[str, List[Union[str, Dict]]]) -> None:
        self.balance = balance
        self.capital = balance
        self.groups: List[Group] = []

        self.init_hierarchy(group_config)

    def set_balance(self, new_balance: float) -> None:
        self.balance = new_balance

    def set_capital(self, new_capital: float) -> None:
        self.capital = new_capital

    def init_hierarchy(self, group_config: Dict[str, List[Union[str, Dict]]]) -> None:
        num_top_groups = len(group_config)
        capital_per_group = self.capital / num_top_groups

        for group_name, contents in group_config.items():
            group = Group(group_name, capital=capital_per_group)
            self._build_group(group, contents, capital_per_group)
            self.groups.append(group)

    def _build_group(self, group: Group, contents: List[Union[str, Dict]], parent_capital: float):
        num_members = len(contents)
        capital_per_member = parent_capital / num_members

        for item in contents:
            if isinstance(item, str):
                instrument = Instrument(item, capital=capital_per_member)
                group.add(instrument)
            elif isinstance(item, dict):
                for sub_group_name, sub_contents in item.items():
                    sub_group = Group(sub_group_name, capital=capital_per_member)
                    self._build_group(sub_group, sub_contents, capital_per_member)
                    group.add(sub_group)

    def get_flat_allocations(self) -> Dict[str, float]:
        result = {}
        for group in self.groups:
            result.update(group.get_flat_allocations())
        return result

    def __repr__(self):
        return f"<Portfolio balance={self.balance} groups={self.groups}>"
