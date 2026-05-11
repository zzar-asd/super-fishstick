#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易计算器小程序
支持加、减、乘、除四则运算
"""

def add(x, y):
    """加法"""
    return x + y

def subtract(x, y):
    """减法"""
    return x - y

def multiply(x, y):
    """乘法"""
    return x * y

def divide(x, y):
    """除法"""
    if y == 0:
        return "错误：除数不能为零！"
    return x / y

def main():
    print("=" * 40)
    print("       欢迎使用简易计算器")
    print("=" * 40)
    
    while True:
        print("\n请选择运算：")
        print("1. 加法 (+)")
        print("2. 减法 (-)")
        print("3. 乘法 (*)")
        print("4. 除法 (/)")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1/2/3/4/5): ")
        
        if choice == '5':
            print("\n感谢使用，再见！")
            break
        
        if choice not in ['1', '2', '3', '4']:
            print("无效的选择，请重新输入！")
            continue
        
        try:
            num1 = float(input("请输入第一个数字: "))
            num2 = float(input("请输入第二个数字: "))
        except ValueError:
            print("错误：请输入有效的数字！")
            continue
        
        if choice == '1':
            result = add(num1, num2)
            operator = "+"
        elif choice == '2':
            result = subtract(num1, num2)
            operator = "-"
        elif choice == '3':
            result = multiply(num1, num2)
            operator = "*"
        elif choice == '4':
            result = divide(num1, num2)
            operator = "/"
        
        print(f"\n结果: {num1} {operator} {num2} = {result}")

if __name__ == "__main__":
    main()
