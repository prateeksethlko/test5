import os
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    app = create_app(os.environ.get('FLASK_ENV', 'production'))
except Exception as e:
    print(f"Failed to create application: {e}")
    exit(1)

# if __name__ == '__main__':
   
#     app.run(
#         host='0.0.0.0',
#         port=5000,
#         debug=False,
#         use_reloader=False
#     )
# if __name__ == '__main__':
#     os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4o"
#     app.run(host='0.0.0.0', port=5000)
if __name__ == '__main__':
    # For Azure App Service
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)