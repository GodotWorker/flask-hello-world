from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from collections import Counter

app = Flask(__name__)

plates = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>License Plate Analytics</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 40px auto;
            background: #fff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .stat-card h2 {
            color: #34495e;
            font-size: 1.2em;
            margin-bottom: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
            </tr>
            {% else %}
            <tr><td colspan="3">No data yet</td></tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, plates=plates)

@app.route('/api/plate', methods=['GET', 'POST'])
def api_plate():
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True) or request.form
        plate = data.get('plate')
        source = data.get('source', 'POST')
    else:
        plate = request.args.get('plate')
        source = request.args.get('source', 'GET')

    if not plate:
        return jsonify({'error': 'Missing plate parameter'}), 400

    entry = {
        'plate': plate,
        'source': source,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    plates.append(entry)
    return jsonify({'status': 'success', 'received': entry})

@app.route('/api/plates')
def get_plates():
    return jsonify(plates)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
