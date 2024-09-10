from flask_mail import Mail, Message
import pandas as pd
from pathlib import Path
import datetime
import os

mail = None

def init_mail(app):
    global mail
    mail = Mail(app)

def convert_to_csv(response):
    file_name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
    file_path = Path(f'./{file_name}').resolve()

    # Convert nodes and edges to DataFrames
    nodes = pd.json_normalize(response['nodes'])
    edges = pd.json_normalize(response['edges'])
    
    # Combine nodes and edges into a single DataFrame
    # Here, we will add a 'source' column to distinguish between nodes and edges
    nodes['node_type'] = 'node'
    edges['node_type'] = 'edge'
    
    # Concatenate both DataFrames
    combined_df = pd.concat([nodes, edges], ignore_index=True)
    
    # Rename columns to remove 'data.' prefix
    combined_df.columns = [col.replace('data.', '') for col in combined_df.columns]

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(file_path, index=False)

    return file_path

def send_email(subject, recipients, body, response):
    attachment_path = None
    try:
        if mail is None:
            raise Exception("Can't send email")
        
        # Create the email message
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
        )
        
        attachment_path = convert_to_csv(response)

        if attachment_path:
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                file_name = attachment_path.name # Get the file name from the path
                msg.attach(file_name, 'application/octet-stream', file_data)

        # Send the email
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        if attachment_path:
            os.remove(attachment_path)        
