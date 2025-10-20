from interactive_dms_service import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=app.config.get('FLASK_ENV') == 'development',
        host='127.0.0.1',
        port=5000
    )
