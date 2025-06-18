"""
Template Processor for deterministic entity generation.

This module provides utilities for processing templates and generating
deterministic, structured entities like passengers, bookings, etc.
"""

from typing import Dict, Any, List, Optional, Union
import random
from datetime import datetime, timedelta
from .data_context_manager import DataContextManager


class TemplateProcessor:
    """Processes templates for deterministic entity generation."""
    
    def __init__(self, data_context_manager: DataContextManager = None, seed: Optional[int] = None):
        """
        Initialize TemplateProcessor.
        
        Args:
            data_context_manager: DataContextManager instance for data resolution
            seed: Random seed for deterministic generation
        """
        self.data_context_manager = data_context_manager or DataContextManager()
        self.template_cache = {}
        self.generated_entities = {}
        
        if seed is not None:
            random.seed(seed)
    
    def process_template(self, template_source: str, instance_index: int = 0, 
                        element_name: str = None) -> Any:
        """
        Process template to generate value for specific instance.
        
        Args:
            template_source: Reference to template data source
            instance_index: Index of the instance to generate
            element_name: Specific element name if processing single field
            
        Returns:
            Generated value from template
        """
        template_data = self.data_context_manager.get_template_data(template_source, instance_index)
        
        if not template_data:
            return None
        
        if element_name:
            # Return specific field from template
            return template_data.get(element_name)
        
        # Return entire template data
        return template_data
    
    def generate_passenger_template(self, instance_index: int, 
                                   template_type: str = 'default') -> Dict[str, Any]:
        """
        Generate a complete passenger template.
        
        Args:
            instance_index: Index of the passenger instance
            template_type: Type of passenger template (business, leisure, family)
            
        Returns:
            Complete passenger data dictionary
        """
        cache_key = f"passenger_{template_type}_{instance_index}"
        
        if cache_key in self.template_cache:
            return self.template_cache[cache_key]
        
        # Predefined passenger templates
        passenger_templates = self._get_passenger_templates()
        
        if template_type in passenger_templates:
            base_templates = passenger_templates[template_type]
            template = base_templates[instance_index % len(base_templates)].copy()
        else:
            # Generate dynamic template
            template = self._generate_dynamic_passenger(instance_index, template_type)
        
        # Process template fields that need computation
        template = self._process_computed_fields(template, instance_index)
        
        self.template_cache[cache_key] = template
        return template
    
    def _get_passenger_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get predefined passenger templates organized by type."""
        return {
            'business': [
                {
                    'template_id': 0,
                    'title': 'Mr',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'passenger_type': 'business',
                    'frequent_flyer': True,
                    'cabin_preference': 'C',
                    'email_domain': 'corporate.com'
                },
                {
                    'template_id': 1,
                    'title': 'Ms',
                    'first_name': 'Sarah',
                    'last_name': 'Johnson',
                    'passenger_type': 'business',
                    'frequent_flyer': True,
                    'cabin_preference': 'F',
                    'email_domain': 'business.com'
                },
                {
                    'template_id': 2,
                    'title': 'Dr',
                    'first_name': 'Michael',
                    'last_name': 'Chen',
                    'passenger_type': 'business',
                    'frequent_flyer': True,
                    'cabin_preference': 'C',
                    'email_domain': 'medical.org'
                }
            ],
            'leisure': [
                {
                    'template_id': 0,
                    'title': 'Ms',
                    'first_name': 'Emily',
                    'last_name': 'Wilson',
                    'passenger_type': 'leisure',
                    'frequent_flyer': False,
                    'cabin_preference': 'Y',
                    'email_domain': 'gmail.com'
                },
                {
                    'template_id': 1,
                    'title': 'Mr',
                    'first_name': 'David',
                    'last_name': 'Brown',
                    'passenger_type': 'leisure',
                    'frequent_flyer': False,
                    'cabin_preference': 'Y',
                    'email_domain': 'yahoo.com'
                },
                {
                    'template_id': 2,
                    'title': 'Mrs',
                    'first_name': 'Lisa',
                    'last_name': 'Davis',
                    'passenger_type': 'leisure',
                    'frequent_flyer': False,
                    'cabin_preference': 'Y',
                    'email_domain': 'hotmail.com'
                }
            ],
            'family': [
                {
                    'template_id': 0,
                    'title': 'Mr',
                    'first_name': 'Robert',
                    'last_name': 'Miller',
                    'passenger_type': 'family',
                    'frequent_flyer': False,
                    'cabin_preference': 'Y',
                    'age_group': 'adult',
                    'family_role': 'parent'
                },
                {
                    'template_id': 1,
                    'title': 'Mrs',
                    'first_name': 'Jennifer',
                    'last_name': 'Miller',
                    'passenger_type': 'family',
                    'frequent_flyer': False,
                    'cabin_preference': 'Y',
                    'age_group': 'adult',
                    'family_role': 'parent'
                },
                {
                    'template_id': 2,
                    'title': 'Miss',
                    'first_name': 'Emma',
                    'last_name': 'Miller',
                    'passenger_type': 'family',
                    'frequent_flyer': False,
                    'cabin_preference': 'Y',
                    'age_group': 'child',
                    'family_role': 'child'
                }
            ]
        }
    
    def _generate_dynamic_passenger(self, instance_index: int, template_type: str) -> Dict[str, Any]:
        """Generate dynamic passenger template when predefined ones don't exist."""
        base_data = {
            'template_id': instance_index,
            'passenger_type': template_type,
            'frequent_flyer': False,
            'cabin_preference': 'Y'
        }
        
        # Get base name data
        titles = ['Mr', 'Ms', 'Mrs', 'Dr', 'Prof']
        first_names = ['Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Quinn']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller']
        
        base_data.update({
            'title': titles[instance_index % len(titles)],
            'first_name': first_names[instance_index % len(first_names)],
            'last_name': last_names[instance_index % len(last_names)]
        })
        
        return base_data
    
    def _process_computed_fields(self, template: Dict[str, Any], instance_index: int) -> Dict[str, Any]:
        """Process fields that need to be computed based on other template data."""
        processed = template.copy()
        
        # Generate email if not present
        if 'email' not in processed and 'first_name' in processed and 'last_name' in processed:
            first_name = processed['first_name'].lower()
            last_name = processed['last_name'].lower()
            domain = processed.get('email_domain', 'email.com')
            processed['email'] = f"{first_name}.{last_name}@{domain}"
        
        # Generate phone if not present
        if 'phone' not in processed:
            # Generate deterministic phone number
            base_phone = 1234567890
            phone_number = base_phone + (instance_index * 111)
            processed['phone'] = f"+{phone_number}"
        
        # Generate passenger ID if not present
        if 'passenger_id' not in processed:
            processed['passenger_id'] = f"PAX{instance_index:03d}"
        
        # Generate date of birth if not present and age group is specified
        if 'date_of_birth' not in processed and 'age_group' in processed:
            processed['date_of_birth'] = self._generate_date_of_birth(
                processed['age_group'], instance_index
            )
        
        return processed
    
    def _generate_date_of_birth(self, age_group: str, instance_index: int) -> str:
        """Generate date of birth based on age group."""
        current_year = datetime.now().year
        
        if age_group == 'child':
            # Children: 2-17 years old
            age = 2 + (instance_index % 16)
        elif age_group == 'adult':
            # Adults: 18-65 years old
            age = 18 + (instance_index % 48)
        elif age_group == 'senior':
            # Seniors: 65+ years old
            age = 65 + (instance_index % 20)
        else:
            # Default adult age
            age = 25 + (instance_index % 40)
        
        birth_year = current_year - age
        # Generate month and day deterministically
        month = 1 + (instance_index % 12)
        day = 1 + (instance_index % 28)  # Safe day range for all months
        
        return f"{birth_year:04d}-{month:02d}-{day:02d}"
    
    def generate_flight_template(self, instance_index: int, route_type: str = 'domestic') -> Dict[str, Any]:
        """
        Generate flight template with realistic flight data.
        
        Args:
            instance_index: Index of the flight instance
            route_type: Type of route (domestic, international, regional)
            
        Returns:
            Complete flight data dictionary
        """
        cache_key = f"flight_{route_type}_{instance_index}"
        
        if cache_key in self.template_cache:
            return self.template_cache[cache_key]
        
        # Get flight data from context or use defaults
        airlines_data = self.data_context_manager.resolve_data_reference('global.airlines')
        if isinstance(airlines_data, dict):
            # Flatten all airline categories
            airlines = []
            for category in airlines_data.values():
                if isinstance(category, list):
                    airlines.extend(category)
        elif isinstance(airlines_data, list):
            airlines = airlines_data
        else:
            airlines = ['AA', 'UA', 'DL', 'WN', 'B6', 'AS', 'NK']
        
        if route_type == 'domestic':
            airports = ['NYC', 'LAX', 'CHI', 'MIA', 'DFW', 'ATL', 'SEA']
        elif route_type == 'international':
            airports = ['NYC', 'LAX', 'LHR', 'CDG', 'FRA', 'NRT', 'SYD']
        else:  # regional
            airports = ['SEA', 'PDX', 'SFO', 'LAX', 'PHX', 'DEN', 'SLC']
        
        # Generate deterministic flight data
        airline = airlines[instance_index % len(airlines)]
        departure_airport = airports[instance_index % len(airports)]
        arrival_airport = airports[(instance_index + 1) % len(airports)]
        
        # Ensure departure != arrival
        if departure_airport == arrival_airport:
            arrival_airport = airports[(instance_index + 2) % len(airports)]
        
        flight_template = {
            'template_id': instance_index,
            'airline': airline,
            'flight_number': f"{airline}{1000 + instance_index}",
            'departure_airport': departure_airport,
            'arrival_airport': arrival_airport,
            'route_type': route_type,
            'aircraft_type': self._get_aircraft_for_route(route_type, instance_index),
            'departure_date': self._generate_flight_date(instance_index),
            'departure_time': self._generate_flight_time(instance_index, 'departure'),
            'arrival_time': self._generate_flight_time(instance_index, 'arrival')
        }
        
        self.template_cache[cache_key] = flight_template
        return flight_template
    
    def _get_aircraft_for_route(self, route_type: str, instance_index: int) -> str:
        """Get appropriate aircraft type for route."""
        aircraft_by_route = {
            'domestic': ['B737', 'A320', 'B757', 'E190'],
            'international': ['B777', 'A330', 'B787', 'A350'],
            'regional': ['E175', 'CRJ900', 'E145', 'ATR72']
        }
        
        aircraft_list = aircraft_by_route.get(route_type, aircraft_by_route['domestic'])
        return aircraft_list[instance_index % len(aircraft_list)]
    
    def _generate_flight_date(self, instance_index: int) -> str:
        """Generate flight date starting from current date + offset."""
        base_date = datetime.now() + timedelta(days=7)  # Start 7 days from now
        flight_date = base_date + timedelta(days=instance_index)
        return flight_date.strftime('%Y-%m-%d')
    
    def _generate_flight_time(self, instance_index: int, time_type: str) -> str:
        """Generate flight time (departure or arrival)."""
        if time_type == 'departure':
            # Generate departure times between 06:00 and 22:00
            base_hour = 6
            hour_range = 16
        else:  # arrival
            # Generate arrival times between 08:00 and 23:59
            base_hour = 8
            hour_range = 16
        
        hour = base_hour + (instance_index % hour_range)
        minute = (instance_index * 15) % 60  # 15-minute intervals
        
        return f"{hour:02d}:{minute:02d}"
    
    def generate_booking_template(self, instance_index: int, booking_type: str = 'standard') -> Dict[str, Any]:
        """
        Generate booking template with complete booking information.
        
        Args:
            instance_index: Index of the booking instance
            booking_type: Type of booking (standard, premium, group)
            
        Returns:
            Complete booking data dictionary
        """
        cache_key = f"booking_{booking_type}_{instance_index}"
        
        if cache_key in self.template_cache:
            return self.template_cache[cache_key]
        
        booking_template = {
            'template_id': instance_index,
            'booking_reference': f"BOOK{instance_index:06d}",
            'booking_type': booking_type,
            'booking_date': self._generate_booking_date(instance_index),
            'passenger_count': self._get_passenger_count_for_booking(booking_type, instance_index),
            'total_amount': self._calculate_booking_amount(booking_type, instance_index),
            'currency': 'USD',
            'status': 'confirmed',
            'payment_method': self._get_payment_method(booking_type, instance_index)
        }
        
        self.template_cache[cache_key] = booking_template
        return booking_template
    
    def _generate_booking_date(self, instance_index: int) -> str:
        """Generate booking date (in the past)."""
        base_date = datetime.now() - timedelta(days=30)  # 30 days ago
        booking_date = base_date + timedelta(days=instance_index % 30)
        return booking_date.strftime('%Y-%m-%d')
    
    def _get_passenger_count_for_booking(self, booking_type: str, instance_index: int) -> int:
        """Get passenger count based on booking type."""
        if booking_type == 'group':
            return 5 + (instance_index % 10)  # 5-14 passengers
        elif booking_type == 'premium':
            return 1 + (instance_index % 3)  # 1-3 passengers
        else:  # standard
            return 1 + (instance_index % 4)  # 1-4 passengers
    
    def _calculate_booking_amount(self, booking_type: str, instance_index: int) -> float:
        """Calculate booking amount based on type and passengers."""
        base_amounts = {
            'standard': 299.99,
            'premium': 899.99,
            'group': 249.99  # Per person discount
        }
        
        base_amount = base_amounts.get(booking_type, 299.99)
        passenger_count = self._get_passenger_count_for_booking(booking_type, instance_index)
        
        # Add some variation
        variation = 1.0 + ((instance_index % 20) - 10) * 0.01  # ±10% variation
        
        return round(base_amount * passenger_count * variation, 2)
    
    def _get_payment_method(self, booking_type: str, instance_index: int) -> str:
        """Get payment method for booking type."""
        if booking_type == 'premium':
            methods = ['amex', 'visa_premium', 'mastercard_platinum']
        elif booking_type == 'group':
            methods = ['corporate_card', 'bank_transfer', 'group_payment']
        else:
            methods = ['visa', 'mastercard', 'paypal', 'debit_card']
        
        return methods[instance_index % len(methods)]
    
    def get_template_summary(self) -> Dict[str, Any]:
        """Get summary of all cached templates."""
        return {
            'cached_templates': len(self.template_cache),
            'template_types': list(set(key.split('_')[0] for key in self.template_cache.keys())),
            'generated_entities': len(self.generated_entities)
        }
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self.template_cache.clear()
        self.generated_entities.clear()