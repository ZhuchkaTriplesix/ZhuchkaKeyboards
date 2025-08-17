"""
Realistic test data generators for performance testing
Creates massive amounts of realistic data for keyboard manufacturing business
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class DataGeneratorConfig:
    """Configuration for data generation"""
    warehouses_count: int = 50
    items_count: int = 10000
    inventory_levels_count: int = 50000
    suppliers_count: int = 200
    purchase_orders_count: int = 1000
    transactions_count: int = 100000


class KeyboardDataGenerator:
    """Generator for realistic keyboard manufacturing data"""
    
    def __init__(self, config: DataGeneratorConfig = None):
        self.config = config or DataGeneratorConfig()
        self._setup_realistic_data()
    
    def _setup_realistic_data(self):
        """Setup realistic data patterns for keyboard manufacturing"""
        
        # Реальные категории клавиатурных компонентов
        self.item_categories = {
            "switches": {
                "types": ["mechanical", "optical", "membrane"],
                "brands": ["Cherry", "Gateron", "Kailh", "Razer", "Logitech", "Outemu", "TTC", "Akko"],
                "switch_types": ["Red", "Blue", "Brown", "Black", "Silver", "Green", "White", "Yellow"],
                "unit_cost_range": (0.5, 3.0),
                "weight_range": (0.005, 0.015)  # kg
            },
            "keycaps": {
                "materials": ["ABS", "PBT", "POM"],
                "profiles": ["OEM", "Cherry", "SA", "XDA", "DSA", "MT3"],
                "colors": ["Black", "White", "Gray", "Blue", "Red", "Purple", "Pink", "Green"],
                "unit_cost_range": (0.1, 2.0),
                "weight_range": (0.001, 0.003)
            },
            "pcb": {
                "types": ["60%", "65%", "75%", "TKL", "Full-size", "40%"],
                "features": ["Hot-swap", "Soldered", "RGB", "Wireless", "USB-C", "South-facing"],
                "brands": ["DZ60", "KBD67", "Tofu", "NK87", "GMMK", "Keychron"],
                "unit_cost_range": (15.0, 80.0),
                "weight_range": (0.05, 0.15)
            },
            "cases": {
                "materials": ["Aluminum", "Plastic", "Wood", "Acrylic", "Carbon Fiber"],
                "colors": ["Black", "Silver", "White", "Blue", "Red", "Purple", "Natural"],
                "layouts": ["60%", "65%", "75%", "TKL", "Full-size", "40%"],
                "unit_cost_range": (20.0, 200.0),
                "weight_range": (0.3, 1.5)
            },
            "stabilizers": {
                "types": ["Cherry", "Durock", "Everglide", "C3", "GMK"],
                "sizes": ["2u", "6.25u", "7u", "2.75u"],
                "materials": ["Plastic", "Aluminum"],
                "unit_cost_range": (0.5, 5.0),
                "weight_range": (0.002, 0.01)
            },
            "cables": {
                "types": ["USB-C", "USB-A", "Coiled", "Straight", "Aviator"],
                "lengths": ["1m", "1.5m", "2m", "3m"],
                "colors": ["Black", "White", "Blue", "Red", "Purple", "Pink"],
                "unit_cost_range": (5.0, 50.0),
                "weight_range": (0.1, 0.3)
            },
            "tools": {
                "types": ["Switch Puller", "Keycap Puller", "Screwdriver", "Lube", "Films", "Springs"],
                "brands": ["Generic", "Keychron", "Glorious", "NK", "Durock"],
                "unit_cost_range": (1.0, 25.0),
                "weight_range": (0.01, 0.5)
            }
        }
        
        # Реальные названия складов
        self.warehouse_names = [
            "Main Distribution Center", "Assembly Plant Alpha", "Component Warehouse North",
            "Quality Control Facility", "Packaging Center", "Raw Materials Storage",
            "Finished Goods Warehouse", "Express Fulfillment Center", "Assembly Plant Beta",
            "Switch Testing Lab", "Keycap Production Facility", "PCB Manufacturing Unit",
            "Case Machining Workshop", "Cable Assembly Line", "Tool Storage Facility",
            "Returns Processing Center", "Bulk Components Storage", "Prototype Workshop",
            "International Shipping Hub", "Local Distribution Point", "Mobile Assembly Unit",
            "Backup Storage Facility", "Seasonal Overflow Warehouse", "Premium Products Vault",
            "Custom Orders Workshop", "Emergency Stock Depot", "Regional Hub East",
            "Regional Hub West", "Regional Hub South", "Supplier Receiving Dock",
            "Quality Assurance Lab", "Research & Development", "Customer Service Center",
            "Repair & Refurbish Center", "Accessory Storage", "Documentation Center",
            "Training Facility", "Environmental Testing Lab", "Automated Sorting Center",
            "Cross-dock Terminal", "Temperature Controlled Storage", "High Security Vault",
            "Prototype Assembly Lab", "Beta Testing Center", "Production Planning Office",
            "Inventory Control Center", "Vendor Management Office", "Logistics Coordination Hub",
            "Emergency Response Depot", "Sustainability Center", "Innovation Workshop"
        ]
        
        # Реальные города и страны для складов
        self.warehouse_locations = [
            {"city": "Shenzhen", "country": "China", "timezone": "Asia/Shanghai"},
            {"city": "Taipei", "country": "Taiwan", "timezone": "Asia/Taipei"}, 
            {"city": "Seoul", "country": "South Korea", "timezone": "Asia/Seoul"},
            {"city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
            {"city": "Singapore", "country": "Singapore", "timezone": "Asia/Singapore"},
            {"city": "Hong Kong", "country": "Hong Kong", "timezone": "Asia/Hong_Kong"},
            {"city": "Los Angeles", "country": "USA", "timezone": "America/Los_Angeles"},
            {"city": "New York", "country": "USA", "timezone": "America/New_York"},
            {"city": "Chicago", "country": "USA", "timezone": "America/Chicago"},
            {"city": "Dallas", "country": "USA", "timezone": "America/Chicago"},
            {"city": "Miami", "country": "USA", "timezone": "America/New_York"},
            {"city": "Seattle", "country": "USA", "timezone": "America/Los_Angeles"},
            {"city": "London", "country": "UK", "timezone": "Europe/London"},
            {"city": "Berlin", "country": "Germany", "timezone": "Europe/Berlin"},
            {"city": "Amsterdam", "country": "Netherlands", "timezone": "Europe/Amsterdam"},
            {"city": "Paris", "country": "France", "timezone": "Europe/Paris"},
            {"city": "Frankfurt", "country": "Germany", "timezone": "Europe/Berlin"},
            {"city": "Stockholm", "country": "Sweden", "timezone": "Europe/Stockholm"},
            {"city": "Sydney", "country": "Australia", "timezone": "Australia/Sydney"},
            {"city": "Melbourne", "country": "Australia", "timezone": "Australia/Melbourne"},
        ]
        
        # Реальные поставщики
        self.supplier_names = [
            "Cherry GmbH", "Gateron Co.", "Kailh Electronics", "JWK Studio", "Durock Manufacturing",
            "TTC Components", "Akko Technology", "Outemu Electronics", "NovelKeys LLC", "KBDfans",
            "Drop Inc.", "Glorious PC Gaming", "Keychron Inc.", "WASD Keyboards", "Ducky Channel",
            "Varmilo Technology", "Leopold Co.", "Filco Corporation", "Topre Corporation", "HHKB",
            "Alps Electric", "Omron Electronics", "GMK Electronic Design", "Signature Plastics",
            "Tai-Hao Enterprise", "Maxkey Technology", "EnjoyPBT", "Infinikey", "ePBT", "CRP",
            "KAT Profile", "MT3 Profile", "XDA Factory", "DSA Manufacturing", "OEM Keycaps Co.",
            "PCB Solutions Ltd", "KiCAD Designs", "Flex Circuit Tech", "Rigid-Flex PCB", "Multi-layer PCB",
            "Hot-swap Sockets Inc", "USB-C Connectors", "LED Components", "Diode Suppliers", "Resistor World",
            "Case Machining Co", "CNC Aluminum Works", "Plastic Injection Ltd", "Acrylic Solutions",
            "Wood Crafters Inc", "Carbon Fiber Tech", "3D Printing Services", "Anodizing Specialists",
            "Powder Coating Inc", "Surface Treatment Co", "Stabilizer Experts", "Mounting Hardware",
            "Screw & Fasteners", "O-Ring Suppliers", "Dampening Materials", "Sound Absorption Co",
            "Cable Assembly LLC", "Connector Specialists", "Wire & Cable Co", "Sleeving Solutions",
            "Heat Shrink Suppliers", "Aviator Connectors", "Coil Cable Makers", "Custom Cable Co",
            "Lube & Film Co", "Switch Modding Supplies", "Springs & Weights", "Gasket Materials",
            "Foam Suppliers", "PE Foam Co", "Poron Foam Ltd", "Silicone Solutions", "Rubber Gaskets",
            "Tool Manufacturing", "Precision Instruments", "Testing Equipment", "Measuring Tools",
            "Assembly Hardware", "Packaging Materials", "Box & Container Co", "Bubble Wrap Suppliers",
            "Label & Sticker Co", "Anti-static Materials", "ESD Protection Inc", "Clean Room Supplies",
            "Quality Control Tools", "Calibration Services", "Testing Protocols", "Certification Bodies"
        ]
    
    def generate_realistic_sku(self, category: str, index: int) -> str:
        """Generate realistic SKU codes"""
        category_codes = {
            "switches": "SW",
            "keycaps": "KC", 
            "pcb": "PCB",
            "cases": "CS",
            "stabilizers": "STB",
            "cables": "CBL",
            "tools": "TL"
        }
        
        code = category_codes.get(category, "ITM")
        year = random.choice([2023, 2024, 2025])
        batch = random.randint(1, 99)
        
        return f"{code}-{year}-{batch:02d}-{index:04d}"
    
    def generate_warehouses(self) -> List[Dict[str, Any]]:
        """Generate realistic warehouse data"""
        warehouses = []
        
        for i in range(self.config.warehouses_count):
            location = random.choice(self.warehouse_locations)
            name = random.choice(self.warehouse_names)
            
            # Убираем использованное название
            if name in self.warehouse_names:
                self.warehouse_names.remove(name)
                if not self.warehouse_names:
                    self.warehouse_names = [f"Warehouse {j}" for j in range(100, 200)]
            
            warehouse = {
                "name": name,
                "code": f"WH-{location['country'][:2].upper()}-{i+1:03d}",
                "description": f"Strategic {name.lower()} located in {location['city']}",
                "address": f"{random.randint(1, 9999)} Industrial Drive",
                "city": location["city"],
                "postal_code": f"{random.randint(10000, 99999)}",
                "country": location["country"],
                "contact_person": f"Manager {chr(65 + i % 26)}. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'])}",
                "phone": f"+{random.randint(1, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "email": f"manager.wh{i+1:03d}@zhuchkakeyboards.com",
                "is_active": random.choices([True, False], weights=[95, 5])[0],  # 95% активных
                "timezone": location["timezone"],
                "capacity_cubic_meters": random.randint(1000, 50000),
                "security_level": random.choice(["Standard", "High", "Maximum"]),
                "climate_controlled": random.choice([True, False])
            }
            warehouses.append(warehouse)
        
        return warehouses
    
    def generate_items(self) -> List[Dict[str, Any]]:
        """Generate realistic item data"""
        items = []
        
        for i in range(self.config.items_count):
            # Выбираем категорию с весами (больше переключателей и клавиш)
            category = random.choices(
                list(self.item_categories.keys()),
                weights=[40, 30, 10, 8, 5, 4, 3]  # switches, keycaps, pcb, cases, stabilizers, cables, tools
            )[0]
            
            category_data = self.item_categories[category]
            
            # Генерируем название в зависимости от категории
            if category == "switches":
                brand = random.choice(category_data["brands"])
                switch_type = random.choice(category_data["switch_types"])
                switch_variant = random.choice(category_data["types"])
                name = f"{brand} {switch_type} {switch_variant.title()} Switch"
                
            elif category == "keycaps":
                material = random.choice(category_data["materials"])
                profile = random.choice(category_data["profiles"])
                color = random.choice(category_data["colors"])
                name = f"{material} {profile} {color} Keycap Set"
                
            elif category == "pcb":
                layout = random.choice(category_data["types"])
                features = random.sample(category_data["features"], random.randint(1, 3))
                brand = random.choice(category_data["brands"])
                name = f"{brand} {layout} PCB ({', '.join(features)})"
                
            elif category == "cases":
                material = random.choice(category_data["materials"])
                color = random.choice(category_data["colors"])
                layout = random.choice(category_data["layouts"])
                name = f"{layout} {material} Case - {color}"
                
            elif category == "stabilizers":
                brand = random.choice(category_data["types"])
                size = random.choice(category_data["sizes"])
                material = random.choice(category_data["materials"])
                name = f"{brand} {size} {material} Stabilizer"
                
            elif category == "cables":
                cable_type = random.choice(category_data["types"])
                length = random.choice(category_data["lengths"])
                color = random.choice(category_data["colors"])
                name = f"{cable_type} {length} Cable - {color}"
                
            else:  # tools
                tool_type = random.choice(category_data["types"])
                brand = random.choice(category_data["brands"])
                name = f"{brand} {tool_type}"
            
            # Генерируем цены и веса
            cost_range = category_data["unit_cost_range"]
            weight_range = category_data["weight_range"]
            
            unit_cost = round(random.uniform(*cost_range), 2)
            selling_price = round(unit_cost * random.uniform(2.0, 4.0), 2)  # markup 200-400%
            weight = round(random.uniform(*weight_range), 4)
            
            # Генерируем уровни запасов
            min_stock = random.randint(10, 500)
            max_stock = min_stock * random.randint(5, 20)
            
            item = {
                "sku": self.generate_realistic_sku(category, i),
                "name": name,
                "description": f"High-quality {name.lower()} for mechanical keyboard enthusiasts and manufacturers",
                "item_type": random.choice(["component", "finished_product", "raw_material"]),
                "category": category,
                "brand": random.choice(category_data.get("brands", ["Generic", "OEM", "Custom"])),
                "model": f"Model-{random.randint(1000, 9999)}",
                "unit_of_measure": "piece",
                "weight_kg": weight,
                "dimensions": f"{random.randint(5, 50)}x{random.randint(5, 50)}x{random.randint(2, 20)} mm",
                "min_stock_level": min_stock,
                "max_stock_level": max_stock,
                "unit_cost": unit_cost,
                "selling_price": selling_price,
                "is_active": random.choices([True, False], weights=[90, 10])[0],  # 90% активных
                "is_tracked": random.choices([True, False], weights=[95, 5])[0],  # 95% отслеживаемых
                "supplier_part_number": f"SPN-{random.randint(100000, 999999)}",
                "barcode": f"{random.randint(1000000000000, 9999999999999)}",
                "lead_time_days": random.randint(1, 30),
                "shelf_life_days": random.choice([None, 365, 730, 1095]),  # Некоторые товары имеют срок годности
                "hazardous": random.choices([True, False], weights=[5, 95])[0],  # 5% опасных
                "temperature_sensitive": random.choices([True, False], weights=[10, 90])[0]
            }
            items.append(item)
        
        return items
    
    def generate_suppliers(self) -> List[Dict[str, Any]]:
        """Generate realistic supplier data"""
        suppliers = []
        
        for i in range(self.config.suppliers_count):
            name = random.choice(self.supplier_names)
            
            # Убираем использованное название
            if name in self.supplier_names:
                self.supplier_names.remove(name)
                if not self.supplier_names:
                    self.supplier_names = [f"Supplier {j}" for j in range(1000, 1200)]
            
            location = random.choice(self.warehouse_locations)
            
            supplier = {
                "name": name,
                "code": f"SUP-{i+1:04d}",
                "description": f"Premium supplier of keyboard components based in {location['city']}",
                "contact_person": f"{random.choice(['Mr.', 'Ms.', 'Dr.'])} {chr(65 + i % 26)}. {random.choice(['Zhang', 'Wang', 'Li', 'Liu', 'Chen', 'Yang', 'Huang', 'Zhao', 'Wu', 'Zhou'])}",
                "email": f"contact@{name.lower().replace(' ', '').replace('.', '')}.com",
                "phone": f"+{random.randint(1, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "address": f"{random.randint(1, 999)} Manufacturing Street",
                "city": location["city"],
                "country": location["country"],
                "postal_code": f"{random.randint(10000, 99999)}",
                "payment_terms": random.choice(["Net 30", "Net 15", "Net 60", "COD", "Prepayment"]),
                "currency": random.choice(["USD", "EUR", "CNY", "JPY", "KRW"]),
                "lead_time_days": random.randint(7, 45),
                "minimum_order_value": random.randint(100, 5000),
                "quality_rating": round(random.uniform(3.0, 5.0), 1),
                "is_active": random.choices([True, False], weights=[85, 15])[0],
                "is_preferred": random.choices([True, False], weights=[20, 80])[0],
                "certification_iso": random.choices([True, False], weights=[70, 30])[0],
                "certification_rohs": random.choices([True, False], weights=[90, 10])[0]
            }
            suppliers.append(supplier)
        
        return suppliers
    
    def generate_inventory_levels(self, warehouses: List[Dict], items: List[Dict]) -> List[Dict[str, Any]]:
        """Generate realistic inventory levels"""
        inventory_levels = []
        
        # Не все товары есть на всех складах
        for warehouse in warehouses:
            # На каждом складе есть 20-80% всех товаров
            warehouse_items = random.sample(items, random.randint(
                int(len(items) * 0.2), 
                int(len(items) * 0.8)
            ))
            
            for item in warehouse_items:
                # Генерируем реалистичные количества
                max_qty = item["max_stock_level"]
                min_qty = item["min_stock_level"]
                
                # Текущее количество (может быть ниже минимума - проблемы с поставками)
                current_qty = random.choices(
                    [
                        random.randint(0, min_qty // 2),  # Низкий остаток
                        random.randint(min_qty, max_qty),  # Нормальный остаток
                        random.randint(max_qty, max_qty * 2)  # Избыток
                    ],
                    weights=[10, 80, 10]  # 10% низкий, 80% нормальный, 10% избыток
                )[0]
                
                # Зарезервированное количество
                reserved_qty = random.randint(0, min(current_qty, current_qty // 4))
                
                # Локации в складе
                zone = random.choice(["A", "B", "C", "D", "E"])
                row = random.randint(1, 20)
                shelf = random.randint(1, 10)
                bin_num = random.randint(1, 50)
                
                level = {
                    "warehouse_code": warehouse["code"],
                    "item_sku": item["sku"],
                    "current_quantity": current_qty,
                    "reserved_quantity": reserved_qty,
                    "location_code": f"{zone}{row:02d}-{shelf:02d}",
                    "bin_location": f"BIN-{bin_num:03d}",
                    "zone_id": f"ZONE-{zone}",
                    "last_counted": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                    "reorder_point": int(min_qty * 1.2),
                    "safety_stock": int(min_qty * 0.3),
                    "abc_classification": random.choices(["A", "B", "C"], weights=[20, 30, 50])[0],
                    "velocity": random.choice(["Fast", "Medium", "Slow"]),
                    "last_movement": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                }
                inventory_levels.append(level)
        
        return inventory_levels
    
    def generate_transactions(self, warehouses: List[Dict], items: List[Dict]) -> List[Dict[str, Any]]:
        """Generate realistic inventory transactions"""
        transactions = []
        
        transaction_types = [
            {"type": "receipt", "reason": "Purchase Order", "weight": 25},
            {"type": "issue", "reason": "Sales Order", "weight": 30},
            {"type": "transfer", "reason": "Warehouse Transfer", "weight": 15},
            {"type": "adjustment", "reason": "Cycle Count", "weight": 10},
            {"type": "return", "reason": "Customer Return", "weight": 8},
            {"type": "scrap", "reason": "Damaged Goods", "weight": 5},
            {"type": "sample", "reason": "Quality Testing", "weight": 4},
            {"type": "promotion", "reason": "Marketing Sample", "weight": 3}
        ]
        
        for i in range(self.config.transactions_count):
            transaction_type = random.choices(
                [t["type"] for t in transaction_types],
                weights=[t["weight"] for t in transaction_types]
            )[0]
            
            reason = next(t["reason"] for t in transaction_types if t["type"] == transaction_type)
            
            warehouse = random.choice(warehouses)
            item = random.choice(items)
            
            # Количество зависит от типа транзакции
            if transaction_type in ["receipt", "return"]:
                quantity = random.randint(10, 1000)  # Положительное для поступлений
            elif transaction_type in ["issue", "scrap", "sample", "promotion"]:
                quantity = -random.randint(1, 500)  # Отрицательное для расходов
            elif transaction_type == "transfer":
                quantity = random.choice([random.randint(1, 200), -random.randint(1, 200)])
            else:  # adjustment
                quantity = random.randint(-100, 100)  # Может быть любым
            
            transaction = {
                "warehouse_code": warehouse["code"],
                "item_sku": item["sku"],
                "quantity": quantity,
                "transaction_type": transaction_type,
                "reason": reason,
                "reference_number": f"{transaction_type.upper()}-{random.randint(100000, 999999)}",
                "unit_cost": item["unit_cost"] * random.uniform(0.9, 1.1),  # Небольшие колебания цены
                "total_cost": abs(quantity) * item["unit_cost"] * random.uniform(0.9, 1.1),
                "transaction_date": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
                "user_id": f"user-{random.randint(1, 50)}",
                "batch_number": f"BATCH-{random.randint(1000, 9999)}",
                "expiry_date": (datetime.now() + timedelta(days=random.randint(30, 720))).isoformat() if random.choice([True, False]) else None,
                "notes": f"Automated {transaction_type} transaction for {reason.lower()}"
            }
            transactions.append(transaction)
        
        return transactions
    
    def save_test_data(self, output_dir: str = "tests/performance/test_data") -> Dict[str, str]:
        """Generate and save all test data to JSON files"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🏭 Generating realistic keyboard manufacturing data...")
        print(f"  Config: {self.config.warehouses_count} warehouses, {self.config.items_count} items")
        
        # Генерируем данные
        warehouses = self.generate_warehouses()
        print(f"  ✅ Generated {len(warehouses)} warehouses")
        
        items = self.generate_items()
        print(f"  ✅ Generated {len(items)} items")
        
        suppliers = self.generate_suppliers() 
        print(f"  ✅ Generated {len(suppliers)} suppliers")
        
        inventory_levels = self.generate_inventory_levels(warehouses, items)
        print(f"  ✅ Generated {len(inventory_levels)} inventory levels")
        
        transactions = self.generate_transactions(warehouses, items)
        print(f"  ✅ Generated {len(transactions)} transactions")
        
        # Сохраняем в файлы
        files = {}
        
        datasets = {
            "warehouses": warehouses,
            "items": items,
            "suppliers": suppliers,
            "inventory_levels": inventory_levels,
            "transactions": transactions
        }
        
        for name, data in datasets.items():
            filepath = os.path.join(output_dir, f"{name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            files[name] = filepath
            print(f"  💾 Saved {len(data)} {name} to {filepath}")
        
        # Генерируем сводку
        summary = {
            "generation_timestamp": datetime.now().isoformat(),
            "config": {
                "warehouses_count": len(warehouses),
                "items_count": len(items),
                "suppliers_count": len(suppliers),
                "inventory_levels_count": len(inventory_levels),
                "transactions_count": len(transactions)
            },
            "statistics": {
                "categories": list(set(item["category"] for item in items)),
                "active_warehouses": len([w for w in warehouses if w["is_active"]]),
                "countries": list(set(w["country"] for w in warehouses)),
                "total_value_estimate": sum(item["unit_cost"] for item in items),
                "files": files
            }
        }
        
        summary_file = os.path.join(output_dir, "summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"  📊 Generated summary: {summary_file}")
        print(f"🎉 Test data generation complete!")
        
        return files


# Convenience functions for different data sizes
def generate_small_dataset() -> KeyboardDataGenerator:
    """Generate small dataset for quick testing"""
    config = DataGeneratorConfig(
        warehouses_count=5,
        items_count=100,
        suppliers_count=20,
        inventory_levels_count=200,
        transactions_count=500
    )
    return KeyboardDataGenerator(config)


def generate_medium_dataset() -> KeyboardDataGenerator:
    """Generate medium dataset for moderate testing"""
    config = DataGeneratorConfig(
        warehouses_count=20,
        items_count=2000,
        suppliers_count=50,
        inventory_levels_count=5000,
        transactions_count=10000
    )
    return KeyboardDataGenerator(config)


def generate_large_dataset() -> KeyboardDataGenerator:
    """Generate large dataset for performance testing"""
    config = DataGeneratorConfig(
        warehouses_count=50,
        items_count=10000,
        suppliers_count=200,
        inventory_levels_count=50000,
        transactions_count=100000
    )
    return KeyboardDataGenerator(config)


def generate_massive_dataset() -> KeyboardDataGenerator:
    """Generate massive dataset for stress testing"""
    config = DataGeneratorConfig(
        warehouses_count=100,
        items_count=50000,
        suppliers_count=500,
        inventory_levels_count=250000,
        transactions_count=1000000
    )
    return KeyboardDataGenerator(config)


if __name__ == "__main__":
    # Генерируем разные размеры данных
    print("🎯 Generating test datasets...")
    
    # Small dataset
    small_gen = generate_small_dataset()
    small_gen.save_test_data("tests/performance/test_data/small")
    
    # Medium dataset  
    medium_gen = generate_medium_dataset()
    medium_gen.save_test_data("tests/performance/test_data/medium")
    
    # Large dataset
    large_gen = generate_large_dataset()
    large_gen.save_test_data("tests/performance/test_data/large")
    
    print("✅ All datasets generated successfully!")
