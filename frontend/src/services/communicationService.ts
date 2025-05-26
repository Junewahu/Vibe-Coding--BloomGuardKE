import axios from 'axios';

interface MessageTemplate {
  id: string;
  name: string;
  content: string;
  type: 'whatsapp' | 'sms' | 'voice';
  language: string;
  variables: string[];
}

interface MessagePayload {
  recipient: string;
  templateId: string;
  variables: Record<string, string>;
  channel: 'whatsapp' | 'sms' | 'voice';
  language: string;
}

class CommunicationService {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    this.apiKey = process.env.REACT_APP_COMMUNICATION_API_KEY || '';
  }

  async sendMessage(payload: MessagePayload): Promise<{ success: boolean; messageId?: string; error?: string }> {
    try {
      const response = await axios.post(`${this.baseUrl}/communications/send`, payload, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      });
      return { success: true, messageId: response.data.messageId };
    } catch (error) {
      console.error('Error sending message:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to send message' 
      };
    }
  }

  async getTemplates(type?: 'whatsapp' | 'sms' | 'voice'): Promise<MessageTemplate[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/communications/templates`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
        params: { type },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching templates:', error);
      return [];
    }
  }

  async createTemplate(template: Omit<MessageTemplate, 'id'>): Promise<MessageTemplate | null> {
    try {
      const response = await axios.post(`${this.baseUrl}/communications/templates`, template, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error creating template:', error);
      return null;
    }
  }

  async getMessageStatus(messageId: string): Promise<{ status: string; deliveredAt?: string; error?: string }> {
    try {
      const response = await axios.get(`${this.baseUrl}/communications/status/${messageId}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching message status:', error);
      return { status: 'unknown', error: 'Failed to fetch status' };
    }
  }
}

export const communicationService = new CommunicationService();
export type { MessageTemplate, MessagePayload }; 