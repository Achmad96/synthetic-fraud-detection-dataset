import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, Tuple

class SAMLDGenerator:
    """Generator for Synthetic Anti-Money Laundering Dataset"""
    
    def __init__(self, seed=42):
        """Initialize the generator with configuration parameters"""
        np.random.seed(seed)
        random.seed(seed)
        
        # Dataset configuration from paper
        self.HIGH_RISK_COUNTRIES = ['Mexico', 'Turkey', 'Morocco', 'United Arab Emirates', 'Panama']
        self.NORMAL_COUNTRIES = ['United Kingdom', 'United States', 'Germany', 'France', 
                                'Canada', 'Australia', 'Japan', 'Spain', 'Italy', 'Netherlands']
        
        self.PAYMENT_TYPES = ['Credit Card', 'Debit Card', 'Cash', 'ACH', 'Cross-border', 'Cheque']
        
        self.CURRENCIES = {
            'United Kingdom': 'GBP',
            'United States': 'USD',
            'Germany': 'EUR',
            'France': 'EUR',
            'Spain': 'EUR',
            'Italy': 'EUR',
            'Netherlands': 'EUR',
            'Canada': 'CAD',
            'Australia': 'AUD',
            'Japan': 'JPY',
            'Mexico': 'MXN',
            'Turkey': 'TRY',
            'Morocco': 'MAD',
            'United Arab Emirates': 'AED',
            'Panama': 'USD'
        }
        
        # 17 Suspicious typologies
        self.SUSPICIOUS_TYPOLOGIES = [
            'Fan-Out', 'Fan-In', 'Cycle', 'Bipartite', 'Stacked Bipartite',
            'Scatter-Gather', 'Gather-Scatter', 'Layered Fan-In', 'Layered Fan-Out',
            'Structuring', 'Smurfing', 'Over-Invoicing', 'Deposit-Send',
            'Cash Withdrawal', 'Single Large Transaction', 'Behavioural Change 1', 
            'Behavioural Change 2'
        ]
        
        # 11 Normal typologies
        self.NORMAL_TYPOLOGIES = [
            'Single Transaction', 'Fan-Out', 'Fan-In', 'Mutual', 'Forward', 
            'Periodical', 'Cash Withdrawal', 'Cash Deposit', 'Small Fan-out',
            'Mutual Plus', 'Normal Group'
        ]
        
        # Account tracking
        self.account_counter = 1000000
        self.normal_accounts = []
        self.suspicious_accounts = []
        self.account_behaviors = {}  # Track normal behavior for behavioral change detection
        
        # Transaction storage
        self.transactions = []
        
    def generate_account_id(self) -> str:
        """Generate unique account ID"""
        self.account_counter += 1
        return f"ACC{self.account_counter:08d}"
    
    def get_currency(self, location: str) -> str:
        """Get currency based on location"""
        return self.CURRENCIES.get(location, 'USD')
    
    def generate_amount(self, typology: str, is_suspicious: bool, layer: int = 0) -> float:
        """Generate transaction amount based on typology"""
        if is_suspicious:
            if typology in ['Structuring', 'Smurfing']:
                # Below reporting threshold (typically $10,000)
                return round(np.random.uniform(5000, 9900), 2)
            elif typology == 'Single Large Transaction':
                return round(np.random.uniform(50000, 500000), 2)
            elif typology in ['Cash Withdrawal', 'Deposit-Send']:
                return round(np.random.uniform(100, 5000), 2)
            elif typology in ['Layered Fan-In', 'Layered Fan-Out']:
                # Amount varies by layer (10-20% change per layer)
                base = np.random.uniform(1000, 50000)
                variation = np.random.uniform(0.9, 1.2) ** layer
                return round(base * variation, 2)
            else:
                return round(np.random.uniform(1000, 100000), 2)
        else:
            # Normal transactions
            if typology in ['Cash Withdrawal', 'Cash Deposit']:
                return round(np.random.uniform(50, 2000), 2)
            elif typology == 'Single Transaction':
                return round(np.random.uniform(10, 5000), 2)
            else:
                return round(np.random.uniform(100, 10000), 2)
    
    def generate_timestamp(self, base_date: datetime, max_days: int = 365) -> Tuple[str, str]:
        """Generate random timestamp within range"""
        days_offset = np.random.randint(0, max_days)
        hours_offset = np.random.randint(0, 24)
        minutes_offset = np.random.randint(0, 60)
        
        timestamp = base_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
        
        date_str = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H:%M:%S')
        
        return date_str, time_str
    
    def create_transaction(self, sender: str, receiver: str, amount: float, 
                          payment_type: str, sender_location: str, receiver_location: str,
                          typology: str, is_suspicious: bool, timestamp: datetime) -> Dict:
        """Create a single transaction record"""
        date_str, time_str = timestamp.strftime('%Y-%m-%d'), timestamp.strftime('%H:%M:%S')
        
        return {
            'Date': date_str,
            'Time': time_str,
            'Sender': sender,
            'Receiver': receiver,
            'Amount': amount,
            'Payment Type': payment_type,
            'Sender Bank Location': sender_location,
            'Receiver Bank Location': receiver_location,
            'Payment Currency': self.get_currency(sender_location),
            'Receiver Currency': self.get_currency(receiver_location),
            'Is Suspicious': 1 if is_suspicious else 0,
            'Type': typology
        }
    
    # ===== SUSPICIOUS TYPOLOGIES =====
    
    def generate_fan_out_suspicious(self, num_instances: int, base_date: datetime):
        """Fan-Out: One account sends to multiple accounts"""
        for _ in range(num_instances):
            sender = self.generate_account_id()
            self.suspicious_accounts.append(sender)
            
            num_receivers = np.random.randint(5, 15)
            sender_location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(self.PAYMENT_TYPES)
            
            # Higher chance of high-risk location
            if np.random.random() < 0.3:
                receiver_location = random.choice(self.HIGH_RISK_COUNTRIES)
            else:
                receiver_location = random.choice(self.NORMAL_COUNTRIES)
            
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            for i in range(num_receivers):
                receiver = self.generate_account_id()
                self.suspicious_accounts.append(receiver)
                
                amount = self.generate_amount('Fan-Out', True)
                timestamp = base_timestamp + timedelta(hours=i)
                
                self.transactions.append(
                    self.create_transaction(sender, receiver, amount, payment_type,
                                          sender_location, receiver_location,
                                          'Fan-Out', True, timestamp)
                )
    
    def generate_fan_in_suspicious(self, num_instances: int, base_date: datetime):
        """Fan-In: Multiple accounts send to one account"""
        for _ in range(num_instances):
            receiver = self.generate_account_id()
            self.suspicious_accounts.append(receiver)
            
            num_senders = np.random.randint(5, 15)
            receiver_location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(self.PAYMENT_TYPES)
            
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            for i in range(num_senders):
                sender = self.generate_account_id()
                self.suspicious_accounts.append(sender)
                
                if np.random.random() < 0.3:
                    sender_location = random.choice(self.HIGH_RISK_COUNTRIES)
                else:
                    sender_location = random.choice(self.NORMAL_COUNTRIES)
                
                amount = self.generate_amount('Fan-In', True)
                timestamp = base_timestamp + timedelta(hours=i)
                
                self.transactions.append(
                    self.create_transaction(sender, receiver, amount, payment_type,
                                          sender_location, receiver_location,
                                          'Fan-In', True, timestamp)
                )
    
    def generate_cycle_suspicious(self, num_instances: int, base_date: datetime):
        """Cycle: Money flows in a circle back to original account"""
        for _ in range(num_instances):
            num_accounts = np.random.randint(3, 7)
            accounts = [self.generate_account_id() for _ in range(num_accounts)]
            self.suspicious_accounts.extend(accounts)
            
            payment_type = random.choice(self.PAYMENT_TYPES)
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            # Create cycle
            for i in range(num_accounts):
                sender = accounts[i]
                receiver = accounts[(i + 1) % num_accounts]
                
                location = random.choice(self.NORMAL_COUNTRIES)
                amount = self.generate_amount('Cycle', True)
                timestamp = base_timestamp + timedelta(days=i)
                
                self.transactions.append(
                    self.create_transaction(sender, receiver, amount, payment_type,
                                          location, location, 'Cycle', True, timestamp)
                )
    
    def generate_layered_fan_in(self, num_instances: int, base_date: datetime):
        """Layered Fan-In: Multiple layers of fan-in transactions"""
        for _ in range(num_instances):
            num_layers = np.random.randint(2, 4)
            accounts_per_layer = [np.random.randint(5, 10) for _ in range(num_layers)]
            
            # Create account structure
            layers = []
            for layer_size in accounts_per_layer:
                layer_accounts = [self.generate_account_id() for _ in range(layer_size)]
                self.suspicious_accounts.extend(layer_accounts)
                layers.append(layer_accounts)
            
            # Final receiver
            final_receiver = self.generate_account_id()
            self.suspicious_accounts.append(final_receiver)
            layers.append([final_receiver])
            
            payment_type = random.choice(self.PAYMENT_TYPES)
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            # Generate transactions between layers
            for layer_idx in range(len(layers) - 1):
                current_layer = layers[layer_idx]
                next_layer = layers[layer_idx + 1]
                
                for sender in current_layer:
                    receiver = random.choice(next_layer)
                    
                    location = random.choice(self.NORMAL_COUNTRIES)
                    amount = self.generate_amount('Layered Fan-In', True, layer_idx)
                    timestamp = base_timestamp + timedelta(days=layer_idx, hours=np.random.randint(0, 24))
                    
                    self.transactions.append(
                        self.create_transaction(sender, receiver, amount, payment_type,
                                              location, location, 'Layered Fan-In', True, timestamp)
                    )
    
    def generate_layered_fan_out(self, num_instances: int, base_date: datetime):
        """Layered Fan-Out: Multiple layers of fan-out transactions"""
        for _ in range(num_instances):
            num_layers = np.random.randint(2, 4)
            accounts_per_layer = [np.random.randint(5, 10) for _ in range(num_layers)]
            
            # Create account structure (reverse of fan-in)
            initial_sender = self.generate_account_id()
            self.suspicious_accounts.append(initial_sender)
            
            layers = [[initial_sender]]
            for layer_size in accounts_per_layer:
                layer_accounts = [self.generate_account_id() for _ in range(layer_size)]
                self.suspicious_accounts.extend(layer_accounts)
                layers.append(layer_accounts)
            
            payment_type = random.choice(self.PAYMENT_TYPES)
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            # Generate transactions between layers
            for layer_idx in range(len(layers) - 1):
                current_layer = layers[layer_idx]
                next_layer = layers[layer_idx + 1]
                
                for sender in current_layer:
                    for receiver in random.sample(next_layer, min(3, len(next_layer))):
                        location = random.choice(self.NORMAL_COUNTRIES)
                        amount = self.generate_amount('Layered Fan-Out', True, layer_idx)
                        timestamp = base_timestamp + timedelta(days=layer_idx, hours=np.random.randint(0, 24))
                        
                        self.transactions.append(
                            self.create_transaction(sender, receiver, amount, payment_type,
                                                  location, location, 'Layered Fan-Out', True, timestamp)
                        )
    
    def generate_structuring(self, num_instances: int, base_date: datetime):
        """Structuring: Breaking large amounts into smaller transactions"""
        for _ in range(num_instances):
            sender = self.generate_account_id()
            receiver = self.generate_account_id()
            self.suspicious_accounts.extend([sender, receiver])
            
            # Multiple small transactions over short period
            num_transactions = np.random.randint(5, 20)
            sender_location = random.choice(self.NORMAL_COUNTRIES)
            receiver_location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(['ACH', 'Cross-border', 'Debit Card'])
            
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            for i in range(num_transactions):
                amount = self.generate_amount('Structuring', True)
                timestamp = base_timestamp + timedelta(hours=i * 2)
                
                self.transactions.append(
                    self.create_transaction(sender, receiver, amount, payment_type,
                                          sender_location, receiver_location,
                                          'Structuring', True, timestamp)
                )
    
    def generate_smurfing(self, num_instances: int, base_date: datetime):
        """Smurfing: Using multiple people to make small deposits"""
        for _ in range(num_instances):
            main_receiver = self.generate_account_id()
            self.suspicious_accounts.append(main_receiver)
            
            num_smurfs = np.random.randint(10, 30)
            receiver_location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(['Cash', 'Debit Card', 'ACH'])
            
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            for i in range(num_smurfs):
                smurf = self.generate_account_id()
                self.suspicious_accounts.append(smurf)
                
                sender_location = random.choice(self.NORMAL_COUNTRIES)
                amount = self.generate_amount('Smurfing', True)
                timestamp = base_timestamp + timedelta(hours=i)
                
                self.transactions.append(
                    self.create_transaction(smurf, main_receiver, amount, payment_type,
                                          sender_location, receiver_location,
                                          'Smurfing', True, timestamp)
                )
    
    def generate_deposit_send(self, num_instances: int, base_date: datetime):
        """Deposit-Send: Quick deposit followed by transfer to high-risk location"""
        for _ in range(num_instances):
            intermediate = self.generate_account_id()
            final_receiver = self.generate_account_id()
            self.suspicious_accounts.extend([intermediate, final_receiver])
            
            location1 = random.choice(self.NORMAL_COUNTRIES)
            # High chance of high-risk location
            location2 = random.choice(self.HIGH_RISK_COUNTRIES) if np.random.random() < 0.7 else random.choice(self.NORMAL_COUNTRIES)
            
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            amount = self.generate_amount('Deposit-Send', True)
            
            # Deposit (cash)
            self.transactions.append(
                self.create_transaction('CASH_DEPOSIT', intermediate, amount, 'Cash',
                                      location1, location1, 'Deposit-Send', True, base_timestamp)
            )
            
            # Quick transfer (within hours)
            transfer_timestamp = base_timestamp + timedelta(hours=np.random.randint(1, 6))
            self.transactions.append(
                self.create_transaction(intermediate, final_receiver, amount * 0.98, 'Cross-border',
                                      location1, location2, 'Deposit-Send', True, transfer_timestamp)
            )
    
    def generate_behavioural_change_1(self, num_instances: int, base_date: datetime):
        """Behavioural Change 1: Account suddenly transacts with new accounts"""
        for _ in range(num_instances):
            main_account = self.generate_account_id()
            self.suspicious_accounts.append(main_account)
            
            # Establish normal pattern first (tracked in account_behaviors)
            core_accounts = [self.generate_account_id() for _ in range(3)]
            self.account_behaviors[main_account] = core_accounts
            
            # Sudden change: new accounts
            new_accounts = [self.generate_account_id() for _ in range(5)]
            self.suspicious_accounts.extend(new_accounts)
            
            location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(self.PAYMENT_TYPES)
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            for new_acc in new_accounts:
                amount = self.generate_amount('Behavioural Change 1', True)
                timestamp = base_timestamp + timedelta(hours=np.random.randint(0, 48))
                
                self.transactions.append(
                    self.create_transaction(main_account, new_acc, amount, payment_type,
                                          location, location, 'Behavioural Change 1', True, timestamp)
                )
    
    def generate_behavioural_change_2(self, num_instances: int, base_date: datetime):
        """Behavioural Change 2: Account suddenly transacts with high-risk locations"""
        for _ in range(num_instances):
            main_account = self.generate_account_id()
            self.suspicious_accounts.append(main_account)
            
            num_new_accounts = np.random.randint(3, 8)
            sender_location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(['Cross-border', 'ACH'])
            
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            for i in range(num_new_accounts):
                new_acc = self.generate_account_id()
                self.suspicious_accounts.append(new_acc)
                
                # High-risk location
                receiver_location = random.choice(self.HIGH_RISK_COUNTRIES)
                amount = self.generate_amount('Behavioural Change 2', True)
                timestamp = base_timestamp + timedelta(days=i)
                
                self.transactions.append(
                    self.create_transaction(main_account, new_acc, amount, payment_type,
                                          sender_location, receiver_location,
                                          'Behavioural Change 2', True, timestamp)
                )
    
    def generate_other_suspicious_typologies(self, num_instances: int, base_date: datetime):
        """Generate other suspicious typologies: Bipartite, Stacked Bipartite, etc."""
        typologies = ['Bipartite', 'Stacked Bipartite', 'Scatter-Gather', 
                     'Gather-Scatter', 'Over-Invoicing', 'Cash Withdrawal', 
                     'Single Large Transaction']
        
        for typology in typologies:
            for _ in range(num_instances):
                sender = self.generate_account_id()
                receiver = self.generate_account_id()
                self.suspicious_accounts.extend([sender, receiver])
                
                sender_location = random.choice(self.NORMAL_COUNTRIES)
                receiver_location = random.choice(self.NORMAL_COUNTRIES)
                
                if typology == 'Cash Withdrawal':
                    payment_type = 'Cash'
                elif typology == 'Over-Invoicing':
                    payment_type = 'Cross-border'
                else:
                    payment_type = random.choice(self.PAYMENT_TYPES)
                
                amount = self.generate_amount(typology, True)
                date_str, time_str = self.generate_timestamp(base_date)
                timestamp = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                
                self.transactions.append(
                    self.create_transaction(sender, receiver, amount, payment_type,
                                          sender_location, receiver_location,
                                          typology, True, timestamp)
                )
    
    # ===== NORMAL TYPOLOGIES =====
    
    def generate_single_transaction(self, num_transactions: int, base_date: datetime):
        """Single Transaction: Normal one-off transactions"""
        for _ in range(num_transactions):
            sender = self.generate_account_id()
            receiver = self.generate_account_id()
            self.normal_accounts.extend([sender, receiver])
            
            sender_location = random.choice(self.NORMAL_COUNTRIES)
            receiver_location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(self.PAYMENT_TYPES)
            
            amount = self.generate_amount('Single Transaction', False)
            date_str, time_str = self.generate_timestamp(base_date)
            timestamp = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
            
            self.transactions.append(
                self.create_transaction(sender, receiver, amount, payment_type,
                                      sender_location, receiver_location,
                                      'Single Transaction', False, timestamp)
            )
    
    def generate_periodical(self, num_instances: int, base_date: datetime):
        """Periodical: Regular recurring transactions (salary, rent, etc.)"""
        for _ in range(num_instances):
            sender = self.generate_account_id()
            receiver = self.generate_account_id()
            self.normal_accounts.extend([sender, receiver])
            
            location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(['ACH', 'Debit Card'])
            
            # Monthly transactions
            num_months = np.random.randint(6, 12)
            base_amount = self.generate_amount('Periodical', False)
            
            for month in range(num_months):
                amount = base_amount * np.random.uniform(0.95, 1.05)  # Slight variation
                timestamp = base_date + timedelta(days=30 * month, hours=np.random.randint(0, 24))
                
                self.transactions.append(
                    self.create_transaction(sender, receiver, amount, payment_type,
                                          location, location, 'Periodical', False, timestamp)
                )
    
    def generate_normal_group(self, num_instances: int, base_date: datetime):
        """Normal Group: Regular account transacting with group of accounts"""
        for _ in range(num_instances):
            main_account = self.generate_account_id()
            core_accounts = [self.generate_account_id() for _ in range(3)]
            regular_accounts = [self.generate_account_id() for _ in range(5)]
            
            self.normal_accounts.extend([main_account] + core_accounts + regular_accounts)
            
            location = random.choice(self.NORMAL_COUNTRIES)
            payment_type = random.choice(self.PAYMENT_TYPES)
            base_timestamp = base_date + timedelta(days=np.random.randint(0, 365))
            
            # Frequent transactions with core accounts
            for core in core_accounts:
                for i in range(np.random.randint(5, 10)):
                    amount = self.generate_amount('Normal Group', False)
                    timestamp = base_timestamp + timedelta(days=i * 7)
                    
                    self.transactions.append(
                        self.create_transaction(main_account, core, amount, payment_type,
                                              location, location, 'Normal Group', False, timestamp)
                    )
            
            # Less frequent transactions with regular accounts
            for reg in regular_accounts:
                for i in range(np.random.randint(1, 3)):
                    amount = self.generate_amount('Normal Group', False)
                    timestamp = base_timestamp + timedelta(days=i * 30)
                    
                    self.transactions.append(
                        self.create_transaction(main_account, reg, amount, payment_type,
                                              location, location, 'Normal Group', False, timestamp)
                    )
    
    def generate_other_normal_typologies(self, num_transactions: int, base_date: datetime):
        """Generate other normal typologies"""
        typologies = ['Fan-Out', 'Fan-In', 'Mutual', 'Forward', 'Cash Withdrawal', 
                     'Cash Deposit', 'Small Fan-out', 'Mutual Plus']
        
        for typology in typologies:
            for _ in range(num_transactions // len(typologies)):
                sender = self.generate_account_id()
                receiver = self.generate_account_id()
                self.normal_accounts.extend([sender, receiver])
                
                location = random.choice(self.NORMAL_COUNTRIES)
                
                if 'Cash' in typology:
                    payment_type = 'Cash'
                else:
                    payment_type = random.choice(self.PAYMENT_TYPES)
                
                amount = self.generate_amount(typology, False)
                date_str, time_str = self.generate_timestamp(base_date)
                timestamp = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                
                self.transactions.append(
                    self.create_transaction(sender, receiver, amount, payment_type,
                                          location, location, typology, False, timestamp)
                )
    
    def generate_dataset(self, total_transactions: int = 100000, 
                        suspicious_ratio: float = 0.05) -> pd.DataFrame:
        """
        Generate complete SAML-D dataset
        
        Args:
            total_transactions: Total number of transactions to generate
            suspicious_ratio: Ratio of suspicious transactions (default 0.124% from paper)
        
        Returns:
            DataFrame with generated transactions
        """
        print(f"Generating SAML-D dataset with {total_transactions:,} transactions...")
        print(f"Target suspicious ratio: {suspicious_ratio * 100:.3f}%")
        
        num_suspicious = int(total_transactions * suspicious_ratio)
        num_normal = total_transactions - num_suspicious
        
        base_date = datetime(2023, 1, 1)
        
        # Generate suspicious transactions
        print("\nGenerating suspicious transactions...")
        suspicious_per_typology = num_suspicious // 17  # 17 suspicious typologies
        
        self.generate_fan_out_suspicious(suspicious_per_typology // 10, base_date)
        self.generate_fan_in_suspicious(suspicious_per_typology // 10, base_date)
        self.generate_cycle_suspicious(suspicious_per_typology // 15, base_date)
        self.generate_layered_fan_in(suspicious_per_typology // 20, base_date)
        self.generate_layered_fan_out(suspicious_per_typology // 20, base_date)
        self.generate_structuring(suspicious_per_typology // 8, base_date)
        self.generate_smurfing(suspicious_per_typology // 10, base_date)
        self.generate_deposit_send(suspicious_per_typology // 5, base_date)
        self.generate_behavioural_change_1(suspicious_per_typology // 15, base_date)
        self.generate_behavioural_change_2(suspicious_per_typology // 15, base_date)
        self.generate_other_suspicious_typologies(suspicious_per_typology // 10, base_date)
        
        # Generate normal transactions
        print("Generating normal transactions...")
        normal_single = num_normal // 2
        normal_periodical = num_normal // 10
        normal_group = num_normal // 20
        normal_other = num_normal - normal_single - normal_periodical - (normal_group * 8)
        
        self.generate_single_transaction(normal_single, base_date)
        self.generate_periodical(normal_periodical, base_date)
        self.generate_normal_group(normal_group, base_date)
        self.generate_other_normal_typologies(normal_other, base_date)
        
        # Create DataFrame
        print("\nCreating DataFrame...")
        df = pd.DataFrame(self.transactions)
        
        # Shuffle transactions
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        return df

generator = SAMLDGenerator(seed=42)
df = generator.generate_dataset(total_transactions=10000, suspicious_ratio=0.05)
df.to_csv('fraud_dataset.csv', index=False)
