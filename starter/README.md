# Udatracker

Udatracker is a minimal order-tracking service built with a framework-agnostic `OrderTracker` core and a Flask API. Keeping validation and business rules in `OrderTracker` leaves the routes responsible only for parsing requests and translating exceptions into HTTP responses. Status updates use copy-update-save behavior so stored order dictionaries are not mutated in place.

The tests also exposed an important integration issue: unit tests using mocked storage did not catch that `OrderTracker` and `InMemoryStorage` originally expected different `save_order` signatures. The next step would be persistent storage, along with a DELETE endpoint and broader API validation tests.

The project structure is:


.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md

