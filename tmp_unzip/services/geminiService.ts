
import { GoogleGenAI, Type, GenerateContentResponse } from "@google/genai";
import { PropertyAnalysis, ImagePreview } from "../types";

export const analyzeProperty = async (text: string, images: ImagePreview[]): Promise<PropertyAnalysis> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
  
  const imageParts = images.map(img => ({
    inlineData: {
      data: img.base64.split(',')[1],
      mimeType: img.mimeType
    }
  }));

  const prompt = `
    Analyze the following Funda.nl property listing data. 
    Extracted text: ${text}
    
    Provide a comprehensive analysis in JSON format based on the text and images.
    Include:
    - A descriptive title and a concise summary.
    - Estimated or listed price history events if found in the text.
    - Sustainability details (energy label, insulation, heating).
    - Neighborhood insights (safety, amenities, character).
    - Any "hidden" details or red flags that a buyer might miss.
  `;

  const response = await ai.models.generateContent({
    model: "gemini-3-pro-preview",
    contents: [
      {
        parts: [
          ...imageParts,
          { text: prompt }
        ]
      }
    ],
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          title: { type: Type.STRING },
          summary: { type: Type.STRING },
          priceHistory: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                event: { type: Type.STRING },
                date: { type: Type.STRING },
                price: { type: Type.STRING }
              }
            }
          },
          sustainability: {
            type: Type.OBJECT,
            properties: {
              label: { type: Type.STRING },
              insulation: { type: Type.STRING },
              potential: { type: Type.STRING }
            }
          },
          neighborhood: {
            type: Type.OBJECT,
            properties: {
              safety: { type: Type.STRING },
              amenities: { type: Type.ARRAY, items: { type: Type.STRING } },
              demographics: { type: Type.STRING }
            }
          },
          hiddenDetails: { type: Type.ARRAY, items: { type: Type.STRING } }
        },
        required: ["title", "summary", "priceHistory", "sustainability", "neighborhood", "hiddenDetails"]
      }
    }
  });

  if (!response.text) {
    throw new Error("No response from AI model");
  }

  return JSON.parse(response.text) as PropertyAnalysis;
};
