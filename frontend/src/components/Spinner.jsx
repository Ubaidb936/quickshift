export default function Spinner({ size = 'md', text = '' }) {
  const sizes = { sm: '1rem', md: '2rem', lg: '3rem' }
  return (
    <div className="spinner-wrapper">
      <div className="spinner" style={{ width: sizes[size], height: sizes[size] }} />
      {text && <p className="spinner-text">{text}</p>}
    </div>
  )
}
