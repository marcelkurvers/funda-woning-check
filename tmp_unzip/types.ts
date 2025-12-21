
export interface PropertyAnalysis {
  title: string;
  summary: string;
  priceHistory: {
    event: string;
    date: string;
    price: string;
  }[];
  sustainability: {
    label: string;
    insulation: string;
    potential: string;
  };
  neighborhood: {
    safety: string;
    amenities: string[];
    demographics: string;
  };
  hiddenDetails: string[];
}

export interface ImagePreview {
  id: string;
  base64: string;
  mimeType: string;
}
