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
        th, td {
            border: 1px solid #eee;
            padding: 15px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: 500;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #f1f4f6;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        .frequency {
            font-weight: bold;
            color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>License Plate Analytics</h1>
        <div class="stats">
            <div class="stat-card">
                <h2>Most Common Plates</h2>
                <table>
                    {% for plate, count in most_common %}
                    <tr>
                        <td>{{ plate }}</td>
                        <td class="frequency">Seen {{ count }} times</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            <div class="stat-card">
                <h2>Recent Activity</h2>
                <table>
                    {% for plate in recent_plates %}
                    <tr>
                        <td>{{ plate.plate }}</td>
                        <td class="timestamp">{{ plate.time_ago }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        
        <table>
            <tr>
                <th>License Plate</th>
                <th>Last Seen</th>
                <th>Frequency</th>
            </tr>
            {% for entry in sorted_plates %}
            <tr>
                <td>{{ entry.plate }}</td>
                <td class="timestamp">{{ entry.last_seen }}</td>
                <td class="frequency">{{ entry.count }} times</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    # Calculate plate frequencies
    plate_counter = Counter(entry['plate'] for entry in plates)
    most_common = plate_counter.most_common(5)
    
    # Format timestamps for recent plates
    recent_plates = []
    for plate in reversed(plates[-5:]):
        time_diff = datetime.now() - datetime.strptime(plate['time'], '%Y-%m-%d %H:%M:%S')
        minutes = time_diff.total_seconds() / 60
        
        if minutes < 60:
            time_ago = f"{int(minutes)} minutes ago"
        elif minutes < 1440:  # 24 hours
            hours = minutes / 60
            time_ago = f"{int(hours)} hours ago"
        else:
            days = int(minutes / 1440)
            time_ago = f"{days} days ago"
            
        recent_plates.append({
            'plate': plate['plate'],
            'time_ago': time_ago
        })
    
    # Create plate summary
    plate_summary = {}
    for entry in plates:
        plate_num = entry['plate']
        if plate_num not in plate_summary:
            plate_summary[plate_num] = {
                'plate': plate_num,
                'count': 0,
                'last_seen': entry['time']
            }
        plate_summary[plate_num]['count'] += 1
        if entry['time'] > plate_summary[plate_num]['last_seen']:
            plate_summary[plate_num]['last_seen'] = entry['time']
    
    sorted_plates = list(plate_summary.values())
    sorted_plates.sort(key=lambda x: x['count'], reverse=True)
    
    return render_template_string(HTML_TEMPLATE, 
                                most_common=most_common,
                                recent_plates=recent_plates,
                                sorted_plates=sorted_plates)

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
        'plate': plate.capitalize(),
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
