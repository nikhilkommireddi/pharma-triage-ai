import { Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { CaseQueue } from './pages/CaseQueue'
import { Dashboard } from './pages/Dashboard'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Dashboard />} />
        <Route path="cases" element={<CaseQueue />} />
      </Route>
    </Routes>
  )
}

export default App
