def test_initiate_b2b_payment_with_empty_request_payload(client):
    """Test initiate b2b payment with empty payload."""
    response = client.post(
        '/api/v1.0/payment/initiate',
        json={}
    )
    assert response.status_code == 400
    assert response.json == {
        'error': 'request is empty.'
    }


def test_initiate_b2b_payment_with_missing_amount_key_in_request_payload(client):
    """Test initiate b2b payment with missing amount in payload."""
    response = client.post(
        '/api/v1.0/payment/initiate',
        json={
            'pnr': '1234567890',
        }
    )
    assert response.status_code == 400
    assert response.json == {
        'error': 'missing key ~ <Amount>.'
    }


def test_initiate_b2b_payment_with_missing_pnr_key_in_request_payload(client):
    """Test initiate b2b payment with missing pnr in payload."""
    response = client.post(
        '/api/v1.0/payment/initiate',
        json={
            'Amount': '100',  # an integer would also work here
        }
    )
    assert response.status_code == 400
    assert response.json == {
        'error': 'missing key ~ <pnr>.'
    }


def test_initiate_b2b_payment_with_invalid_amount(client):
    """Test initiate b2b payment with invalid amount."""
    response = client.post(
        '/api/v1.0/payment/initiate',
        json={
            'Amount': '100xBB3',
            'pnr': '1234567890',
        }
    )
    assert response.status_code == 400
    assert response.json == {
        'error': '<Amount> must be a number.'
    }


def test_initiate_b2b_payment_with_amount_less_than_1(client):
    """Test initiate b2b payment with an amount less than 1."""
    response = client.post(
        '/api/v1.0/payment/initiate',
        json={
            'Amount': '0',  # an integer would also work here
            'pnr': '1234567890',
        }
    )
    assert response.status_code == 400
    assert response.json == {
        'error': '<Amount> cannot be less than or equal to zero.'
    }
