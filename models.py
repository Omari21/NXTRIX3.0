"""
Database models and schema definitions for NXTRIX CRM
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

@dataclass
class Deal:
    id: str
    address: str
    property_type: str
    purchase_price: float
    arv: float
    repair_costs: float
    monthly_rent: float
    closing_costs: float
    annual_taxes: float
    insurance: float
    hoa_fees: float
    vacancy_rate: float
    neighborhood_grade: str
    condition: str
    market_trend: str
    ai_score: int
    status: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    notes: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deal':
        """Create Deal instance from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            address=data.get('address', ''),
            property_type=data.get('property_type', ''),
            purchase_price=float(data.get('purchase_price', 0)),
            arv=float(data.get('arv', 0)),
            repair_costs=float(data.get('repair_costs', 0)),
            monthly_rent=float(data.get('monthly_rent', 0)),
            closing_costs=float(data.get('closing_costs', 0)),
            annual_taxes=float(data.get('annual_taxes', 0)),
            insurance=float(data.get('insurance', 0)),
            hoa_fees=float(data.get('hoa_fees', 0)),
            vacancy_rate=float(data.get('vacancy_rate', 5)),
            neighborhood_grade=data.get('neighborhood_grade', 'B'),
            condition=data.get('condition', 'Good'),
            market_trend=data.get('market_trend', 'Stable'),
            ai_score=int(data.get('ai_score', 0)),
            status=data.get('status', 'New'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            user_id=data.get('user_id'),
            notes=data.get('notes')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Deal instance to dictionary"""
        return {
            'id': self.id,
            'address': self.address,
            'property_type': self.property_type,
            'purchase_price': self.purchase_price,
            'arv': self.arv,
            'repair_costs': self.repair_costs,
            'monthly_rent': self.monthly_rent,
            'closing_costs': self.closing_costs,
            'annual_taxes': self.annual_taxes,
            'insurance': self.insurance,
            'hoa_fees': self.hoa_fees,
            'vacancy_rate': self.vacancy_rate,
            'neighborhood_grade': self.neighborhood_grade,
            'condition': self.condition,
            'market_trend': self.market_trend,
            'ai_score': self.ai_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'user_id': self.user_id,
            'notes': self.notes
        }

@dataclass
class Investor:
    id: str
    name: str
    email: str
    phone: Optional[str]
    investment_range_min: float
    investment_range_max: float
    preferred_markets: str
    deal_types: str
    success_rate: float
    total_investments: int
    status: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    notes: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Investor':
        """Create Investor instance from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            investment_range_min=float(data.get('investment_range_min', 0)),
            investment_range_max=float(data.get('investment_range_max', 0)),
            preferred_markets=data.get('preferred_markets', ''),
            deal_types=data.get('deal_types', ''),
            success_rate=float(data.get('success_rate', 0)),
            total_investments=int(data.get('total_investments', 0)),
            status=data.get('status', 'Active'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            user_id=data.get('user_id'),
            notes=data.get('notes')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Investor instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'investment_range_min': self.investment_range_min,
            'investment_range_max': self.investment_range_max,
            'preferred_markets': self.preferred_markets,
            'deal_types': self.deal_types,
            'success_rate': self.success_rate,
            'total_investments': self.total_investments,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'user_id': self.user_id,
            'notes': self.notes
        }

@dataclass
class Portfolio:
    id: str
    deal_id: str
    investor_id: Optional[str]
    investment_amount: float
    ownership_percentage: float
    entry_date: datetime
    exit_date: Optional[datetime]
    current_value: float
    total_return: float
    status: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Portfolio':
        """Create Portfolio instance from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            deal_id=data.get('deal_id', ''),
            investor_id=data.get('investor_id'),
            investment_amount=float(data.get('investment_amount', 0)),
            ownership_percentage=float(data.get('ownership_percentage', 0)),
            entry_date=data.get('entry_date', datetime.now()),
            exit_date=data.get('exit_date'),
            current_value=float(data.get('current_value', 0)),
            total_return=float(data.get('total_return', 0)),
            status=data.get('status', 'Active'),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            user_id=data.get('user_id')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Portfolio instance to dictionary"""
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'investor_id': self.investor_id,
            'investment_amount': self.investment_amount,
            'ownership_percentage': self.ownership_percentage,
            'entry_date': self.entry_date.isoformat() if isinstance(self.entry_date, datetime) else self.entry_date,
            'exit_date': self.exit_date.isoformat() if isinstance(self.exit_date, datetime) and self.exit_date else self.exit_date,
            'current_value': self.current_value,
            'total_return': self.total_return,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'user_id': self.user_id
        }