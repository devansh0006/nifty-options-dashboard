from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import seaborn as sns
from datetime import datetime, timedelta

app = Flask(__name__)

# Custom filter for number formatting
@app.template_filter('format_number')
def format_number(value):
    return "{:,}".format(value)

# Configure matplotlib
plt.switch_backend('Agg')
sns.set_style("whitegrid")

def process_data():
    df = pd.read_csv('data/nifty_options_20_09_2024.csv')
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df.sort_values('datetime', inplace=True)
    
    # Calculate additional metrics
    df['daily_return'] = df['close'].pct_change() * 100
    df['price_range'] = df['high'] - df['low']
    return df

def create_plot(df, plot_type, symbol=None):
    plt.figure(figsize=(10, 6))
    
    if plot_type == 'distribution':
        sns.histplot(df['close'], bins=30, kde=True, color='#6366f1')
        plt.title('Closing Price Distribution', fontsize=14, pad=20)
        plt.xlabel('Price', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        
    elif plot_type == 'timeseries':
        if not symbol:
            symbol = df['symbol'].iloc[0]
        symbol_df = df[df['symbol'] == symbol]
        plt.plot(symbol_df['datetime'], symbol_df['close'], 
                marker='o', markersize=4, linestyle='-', 
                color='#3b82f6', linewidth=2)
        plt.title(f'{symbol} Price Trend', fontsize=14, pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.xticks(rotation=45)
        
    elif plot_type == 'volume_oi':
        sns.scatterplot(x='volume', y='oi', data=df, 
                       color='#10b981', alpha=0.7, s=100)
        plt.title('Volume vs. Open Interest', fontsize=14, pad=20)
        plt.xlabel('Volume', fontsize=12)
        plt.ylabel('Open Interest', fontsize=12)
        
    elif plot_type == 'correlation':
        numeric_cols = ['open', 'high', 'low', 'close', 'oi', 'volume']
        sns.heatmap(df[numeric_cols].corr(), annot=True, 
                   cmap='coolwarm', fmt=".2f", 
                   annot_kws={"size": 10}, cbar=False)
        plt.title('Feature Correlation', fontsize=14, pad=20)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        
    elif plot_type == 'returns':
        sns.histplot(df['daily_return'].dropna(), bins=30, 
                     kde=True, color='#8b5cf6')
        plt.title('Daily Returns Distribution', fontsize=14, pad=20)
        plt.xlabel('Return (%)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        
    plt.tight_layout()
    
    # Save plot to bytes
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

@app.route('/')
def dashboard():
    df = process_data()
    
    # Get unique symbols for dropdown
    symbols = df['symbol'].unique().tolist()
    
    # Create plots
    plots = {
        'distribution': create_plot(df, 'distribution'),
        'timeseries': create_plot(df, 'timeseries'),
        'volume_oi': create_plot(df, 'volume_oi'),
        'correlation': create_plot(df, 'correlation'),
        'returns': create_plot(df, 'returns')
    }
    
    # Calculate statistics
    stats = {
        'start_date': df['datetime'].min().strftime('%b %d, %Y'),
        'end_date': df['datetime'].max().strftime('%b %d, %Y'),
        'num_records': len(df),
        'symbols': df['symbol'].nunique(),
        'avg_volume': int(df['volume'].mean()),
        'avg_oi': int(df['oi'].mean()),
        'last_close': round(df.iloc[-1]['close'], 2),
        'max_close': round(df['close'].max(), 2),
        'min_close': round(df['close'].min(), 2)
    }
    
    return render_template('index.html', 
                         plots=plots, 
                         stats=stats,
                         symbols=symbols)

@app.route('/update_plot/<symbol>')
def update_plot(symbol):
    df = process_data()
    plot = create_plot(df, 'timeseries', symbol)
    return jsonify({'plot': plot})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)