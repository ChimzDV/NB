from flask import Blueprint, jsonify, request

loan_bp = Blueprint('loans', __name__)

@loan_bp.route('/', methods=['GET'])
def get_loans():
    """Retrieve all loans for the authenticated user."""
    # Starter placeholder logic
    return jsonify({
        "loans": [],
        "count": 0,
        "message": "Loan retrieval endpoint working (empty starter list)"
    }), 200

@loan_bp.route('/apply', methods=['POST'])
def apply_loan():
    """Submit a new loan application."""
    # Starter placeholder logic
    data = request.get_json() or {}
    amount = data.get('amount')
    
    if not amount:
        return jsonify({"error": "Loan amount is required"}), 400
        
    return jsonify({
        "message": "Loan application submitted successfully",
        "amount": amount,
        "status": "pending_review"
    }), 201
