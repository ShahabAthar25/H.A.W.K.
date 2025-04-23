from typing import Dict, List
from datetime import datetime


class Position:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0.0
        self.avg_price = 0.0
        self.current_price = 0.0

        self.entry_timestamps: List[datetime] = []
        self.cumulative_cost = 0.0
        self.realized_pnl = 0.0

    def update(self, price: float, qty: float, timestamp: datetime = None):
        if qty == 0:
            return

        direction = 1 if qty > 0 else -1

        # Same direction (increase position)
        if self.quantity * qty > 0:
            total_value = self.avg_price * abs(self.quantity) + price * abs(qty)
            self.quantity += qty
            self.avg_price = total_value / abs(self.quantity)
            self.cumulative_cost += direction * price * abs(qty)
            self.entry_timestamps.append(timestamp or datetime.now())

        # Reducing position (partial/full close)
        elif self.quantity * qty < 0:
            closing_qty = min(abs(qty), abs(self.quantity))
            pnl = (price - self.avg_price) * closing_qty * (-direction)
            self.realized_pnl += pnl
            self.cumulative_cost -= self.avg_price * closing_qty
            self.quantity += qty  # qty is negative here

            if self.quantity == 0:
                self.avg_price = 0.0
                self.entry_timestamps.clear()

        elif self.quantity == 0:
            self.avg_price = price
            self.quantity = qty
            self.cumulative_cost = direction * price * abs(qty)
            self.entry_timestamps = [timestamp or datetime.now()]

    def close(self, price: float, timestamp: datetime = None):
        if self.quantity == 0:
            return
        self.update(price, -self.quantity, timestamp)

    def mark_price(self, price: float):
        self.current_price = price

    def unrealized_pnl(self) -> float:
        return (self.current_price - self.avg_price) * self.quantity

    def value(self) -> float:
        return self.current_price * self.quantity

    def is_open(self):
        return self.quantity != 0


class TradeExecutor:
    def __init__(self):
        self.positions: Dict[str, Position] = {}

    def execute(self, symbol: str, price: float, quantity: float, timestamp: datetime):
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)
        self.positions[symbol].update(price, quantity, timestamp)

    def close(self, symbol: str, price: float, timestamp: datetime = None):
        if symbol in self.positions and self.positions[symbol].is_open():
            self.positions[symbol].close(price, timestamp)

    def mark_market_price(self, symbol: str, price: float):
        if symbol in self.positions:
            self.positions[symbol].mark_price(price)

    def get_position(self, symbol: str) -> Position:
        return self.positions.get(symbol, None)
    
    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions and self.positions[symbol].is_open()

    def summary(self):
        print("=== Positions Summary ===")
        for symbol, pos in self.positions.items():
            if pos.is_open():
                print(
                    f"{symbol}: Qty={pos.quantity:.4f}, "
                    f"AvgPrice={pos.avg_price:.2f}, "
                    f"CurPrice={pos.current_price:.2f}, "
                    f"Value={pos.value():.2f}, "
                    f"UnrealizedPnL={pos.unrealized_pnl():.2f}, "
                    f"RealizedPnL={pos.realized_pnl:.2f}, "
                    f"Entries={len(pos.entry_timestamps)}"
                )
            else:
                print(
                    f"{symbol}: CLOSED | RealizedPnL={pos.realized_pnl:.2f}"
                )
