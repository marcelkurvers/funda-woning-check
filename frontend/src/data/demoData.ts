import type { ChapterData } from '../types';

export const DEMO_CHAPTER: ChapterData = {
    id: "2",
    title: "Locatie & Omgeving",
    intro: "Een diepgaande analyse van de directe omgeving, voorzieningen en bereikbaarheid van Hondelburg 27.",
    main_analysis: `
    <p>De woning aan de Hondelburg 27 is gelegen in een rustige, groene wijk die bekend staat om zijn kindvriendelijke karakter. Uit de data blijkt dat de wijk een hoge score scoort op leefbaarheid, mede dankzij de ruime opzet en de aanwezigheid van diverse parken in de directe nabijheid.</p>
    <h3>Voorzieningen</h3>
    <p>Op loopafstand bevinden zich diverse basisscholen en een kleinschalig winkelcentrum voor de dagelijkse boodschappen. Voor uitgebreider winkelen is het stadscentrum op slechts 10 minuten fietsen bereikbaar. De dichtheid van horeca is in de directe straat beperkt, wat bijdraagt aan de rust, maar wel betekent dat voor vertier iets verder gereisd moet worden.</p>
    <h3>Bereikbaarheid</h3>
    <p>De aansluiting op de ringweg is uitstekend, met een oprit op slechts 3 minuten rijden. Het openbaar vervoer is eveneens goed vertegenwoordigd met een bushalte om de hoek en een treinstation op 1.5 km afstand.</p>
  `,
    conclusion: "Een toplocatie voor gezinnen die rust zoeken maar toch dicht bij stedelijke voorzieningen willen wonen.",
    interpretation: "De locatiebalans is uitzonderlijk positief: 85% van de voorzieningen ligt binnen de ideale 15-minuten zone. Dit maakt de woning zeer toekomstbestendig.",
    strengths: [
        "Gelegen in een groene, rustige wijk",
        "Uitstekende bereikbaarheid via uitvalswegen",
        "Winkelcentrum op loopafstand"
    ],
    advice: [
        "Houd rekening met mogelijke parkeerdrukte in het weekend",
        "Geluid van de nabijgelegen spoorlijn kan bij oostenwind hoorbaar zijn"
    ],
    sidebar_items: [
        {
            type: 'advisor_score',
            title: 'Locatiescore',
            score: 88,
            content: 'Deze locatie scoort in de top 10% van vergelijkbare woningen in de regio.'
        },
        {
            type: 'action_list',
            title: 'Buurt Check',
            items: [
                'Controleer bestemmingsplan braakliggend terrein',
                'Check parkeervergunning beleid'
            ]
        }
    ]
};

export const DEMO_REPORT = {
    address: "Hondelburg 27, 2135 VB Hoofddorp",
    chapters: {
        "0": {
            ...DEMO_CHAPTER,
            id: "0",
            title: "Executive Summary",
            intro: "Samenvatting van de belangrijkste bevindingen.",
            conclusion: "Positief advies met enkele aandachtspunten.",
        },
        "1": {
            ...DEMO_CHAPTER,
            id: "1",
            title: "Algemene kenmerken",
            intro: "Overzicht van de woningkenmerken.",
        },
        "2": DEMO_CHAPTER,
        "3": {
            ...DEMO_CHAPTER,
            id: "3",
            title: "Waarde-inschatting",
            intro: "Analyse van de marktwaarde.",
        },
        "4": { ...DEMO_CHAPTER, id: "4", title: "Markttijd & Prijs" },
        "5": { ...DEMO_CHAPTER, id: "5", title: "Onderhandeling" },
        "6": { ...DEMO_CHAPTER, id: "6", title: "Kosten & TCO" },
        "7": { ...DEMO_CHAPTER, id: "7", title: "Omgeving" },
        "8": { ...DEMO_CHAPTER, id: "8", title: "Advies" },
        "9": { ...DEMO_CHAPTER, id: "9", title: "Bodstrategie" },
        "10": { ...DEMO_CHAPTER, id: "10", title: "KPI Benchmark" },
        "11": { ...DEMO_CHAPTER, id: "11", title: "Renovatie" },
        "12": { ...DEMO_CHAPTER, id: "12", title: "Marktgevoel" }
    }
};
