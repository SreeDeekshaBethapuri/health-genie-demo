import HealthGenieWidget from "../components/HealthGenieWidget";

const CARDS = [
  {
    title: "Wellness Assessment",
    description: "Understand your health baseline and get personalized guidance.",
    icon: "🩺",
  },
  {
    title: "At-home Testing",
    description: "Order a kit, collect a sample, and get results delivered online.",
    icon: "🧪",
  },
  {
    title: "Supplements",
    description: "Explore targeted supplements matched to your wellness goals.",
    icon: "💊",
  },
  {
    title: "Virtual Care",
    description: "Connect with a provider for personalized health support.",
    icon: "💬",
  },
];

export default function Home() {
  return (
    <>
      <header style={styles.header}>
        <span style={styles.logo}>Health Vibe</span>
      </header>

      <main style={styles.main}>
        <section style={styles.hero}>
          <h1 style={styles.heroTitle}>Your personal health journey starts here</h1>
          <p style={styles.heroSub}>
            Use Health Genie to get guided support for wellness, supplements,
            virtual care, and kit registration.
          </p>
        </section>

        <section style={styles.grid}>
          {CARDS.map((card) => (
            <div key={card.title} style={styles.card}>
              <span style={styles.cardIcon}>{card.icon}</span>
              <h3 style={styles.cardTitle}>{card.title}</h3>
              <p style={styles.cardDesc}>{card.description}</p>
            </div>
          ))}
        </section>
      </main>

      <HealthGenieWidget />
    </>
  );
}

const styles: Record<string, React.CSSProperties> = {
  header: {
    background: "#fff",
    borderBottom: "1px solid var(--border)",
    padding: "0 24px",
    height: 56,
    display: "flex",
    alignItems: "center",
    boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
  },
  logo: {
    fontSize: 20,
    fontWeight: 700,
    color: "var(--purple)",
    letterSpacing: "-0.3px",
  },
  main: {
    maxWidth: 960,
    margin: "0 auto",
    padding: "48px 24px 120px",
  },
  hero: {
    textAlign: "center",
    marginBottom: 48,
  },
  heroTitle: {
    fontSize: "clamp(24px, 4vw, 36px)",
    fontWeight: 700,
    color: "var(--text)",
    lineHeight: 1.25,
    marginBottom: 12,
  },
  heroSub: {
    fontSize: 16,
    color: "var(--text-muted)",
    maxWidth: 560,
    margin: "0 auto",
    lineHeight: 1.6,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: 20,
  },
  card: {
    background: "#fff",
    borderRadius: 12,
    padding: "24px 20px",
    boxShadow: "var(--shadow)",
    display: "flex",
    flexDirection: "column",
    gap: 10,
    border: "1px solid var(--border)",
  },
  cardIcon: {
    fontSize: 28,
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: 600,
    color: "var(--text)",
  },
  cardDesc: {
    fontSize: 13,
    color: "var(--text-muted)",
    lineHeight: 1.5,
  },
};
