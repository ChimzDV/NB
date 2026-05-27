class LoanService:
    """Service to handle core financial calculations and loan processing workflows."""

    @staticmethod
    def calculate_monthly_payment(principal, annual_interest_rate, term_months):
        """
        Calculate standard monthly payment using the amortization formula:
        M = P * [ r(1+r)^n ] / [ (1+r)^n - 1 ]
        where:
        M = Monthly payment
        P = Principal amount
        r = Monthly interest rate (annual_interest_rate / 12 / 100)
        n = Number of monthly payments (term_months)
        """
        if principal <= 0 or term_months <= 0:
            return 0.0
            
        if annual_interest_rate == 0:
            return float(principal / term_months)

        monthly_rate = (annual_interest_rate / 100.0) / 12.0
        numerator = monthly_rate * ((1.0 + monthly_rate) ** term_months)
        denominator = ((1.0 + monthly_rate) ** term_months) - 1.0
        
        monthly_payment = principal * (numerator / denominator)
        return round(monthly_payment, 2)

    @staticmethod
    def generate_amortization_schedule(principal, annual_interest_rate, term_months):
        """Generate monthly amortization breakdown including Principal vs Interest portion."""
        monthly_payment = LoanService.calculate_monthly_payment(principal, annual_interest_rate, term_months)
        monthly_rate = (annual_interest_rate / 100.0) / 12.0
        
        balance = float(principal)
        schedule = []
        
        for month in range(1, term_months + 1):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment
            
            # Prevent minor floating point inaccuracies at the final month
            if month == term_months or balance < 0:
                principal_payment += balance
                balance = 0.0

            schedule.append({
                "month": month,
                "monthly_payment": round(monthly_payment, 2),
                "principal_payment": round(principal_payment, 2),
                "interest_payment": round(interest_payment, 2),
                "remaining_balance": round(max(balance, 0.0), 2)
            })
            
        return schedule
