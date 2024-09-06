from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import geopandas as gpd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Read the CSV and convert to SHP
        data = pd.read_csv(filepath)
        gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['X1'], data['Y1']))
        
        output_shp = os.path.join(app.config['OUTPUT_FOLDER'], file.filename.replace('.csv', '.shp'))
        gdf.to_file(output_shp)
        
        return send_file(output_shp, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
