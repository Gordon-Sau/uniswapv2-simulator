from typing import Tuple
from math import sqrt

class Pair:
    def __init__(self):
        self.reserve0: float = 0
        self.reserve1: float = 0
        self.liquiditySupply: float = 0
        self.kLast: float = 0

    def _mintFee(self)->float:
        print(f"kLast: {self.kLast}")
        if self.kLast != 0:
            rootKLast = sqrt(self.kLast)
            rootK = sqrt(self.reserve0 * self.reserve1)
            if (rootK > rootKLast):
                fee = self.liquiditySupply * (rootK - rootKLast) / (5 * rootK + rootKLast)
                if (fee > 0):
                    self.liquiditySupply += fee
                    return fee
                else:
                    print(f"fee = {fee} <= 0")
        return 0

    def _mint(self, amount0:float, amount1: float)->float:
        if self.liquiditySupply == 0:
            self.liquiditySupply = sqrt(amount0 * amount1)
            self.reserve0 += amount0
            self.reserve1 += amount1
            self.kLast = self.reserve0 * self.reserve1
            return self.liquiditySupply
        else:
            print(f"factor0:{amount0 / self.reserve0}    factor1:{amount1 / self.reserve1}")
            liquidityAmount = min(
                amount0 / self.reserve0,
                amount1 / self.reserve1
            ) * self.liquiditySupply
            self.liquiditySupply += liquidityAmount
            self.reserve0 += amount0
            self.reserve1 += amount1
            self.kLast = self.reserve0 * self.reserve1
            return liquidityAmount

    def addLiquidity(self, amount0: float, amount1: float)->Tuple[float, float]:
        if self.liquiditySupply != 0:
            liquidityAmount: float
            factor = amount0 / self.reserve0
            amount1Required = self.reserve1 * factor
            if amount1Required > amount1:
                factor = amount1 / self.reserve1
                amount0Required = factor * self.reserve0
                assert(amount0Required <= amount0)
                print(f"user deposits {amount0Required} token0s and {amount1} token1s")
                amount0 = amount0Required
            else:
                print(f"user deposits {amount0} token0s and {amount1Required} token1s")
                amount1 = amount1Required

        fee = self._mintFee()
        liquidityAmount = self._mint(amount0, amount1)
        return liquidityAmount, fee

    def removeLiquidity(self, liquidityAmount: float)->Tuple[float, float, float]:
        assert(liquidityAmount <= self.liquiditySupply)
        fee = self._mintFee()
        amount0 = liquidityAmount * self.reserve0 / self.liquiditySupply
        amount1 = liquidityAmount * self.reserve1 / self.liquiditySupply
        self.liquiditySupply -= liquidityAmount
        self.reserve0 -= amount0
        self.reserve1 -= amount1
        self.kLast = self.reserve0 * self.reserve1
        return (amount0, amount1, fee)
    
    def swapIn(self, tokenType: int, amount: float)->float:
        if (tokenType % 2) == 0:
            amount1 = amount * self.reserve1 * 997/ (self.reserve0 * 1000 + amount * 997)
            assert (self.reserve1 >= amount1)
            self.reserve0 += amount
            self.reserve1 -= amount1
            return amount1
        else:
            amount0 = amount * self.reserve0 * 997 / (self.reserve1 * 1000 + amount * 997)
            assert (self.reserve0 >= amount0)
            self.reserve0 -= amount0
            self.reserve1 += amount
            return amount0

def transact(pair: Pair):
    inputTxt = input()
    inputs = inputTxt.split()
    if inputs[0].lower()[0] == "a":
        print("add liquidity:")
        (liquidityAmount, fee) = pair.addLiquidity(float(inputs[1]), float(inputs[2]))
        print(f"user recieves {liquidityAmount} liquidity tokens")
        print(f"{fee} is charged as protocol fee")
    elif inputs[0].lower()[0] == "r":
        print("remove liquidity:")
        (amount0, amount1, fee) = pair.removeLiquidity(float(inputs[1]))
        print(f"user receives {amount0} token0s and {amount1} token1s")
        print(f"{fee} is charged as protocol fee")
    elif inputs[0].lower()[0] == "s":
        print("swap:")
        outputTokenAmount = pair.swapIn(int(inputs[1]), float(inputs[2]))
        print(f"user receives {outputTokenAmount} token{((int(inputs[1])+1)%2)}s")

if __name__ == "__main__":
    pair = Pair()
    while True:
        try:
            transact(pair)
            print(f"reserve0: {pair.reserve0}    reserve1: {pair.reserve1}    liquiditySupply: {pair.liquiditySupply}\n")
        except EOFError:
            break
