import { QueryProvider } from './providers/QueryProvider';
import { Layout } from './components';
import { Dashboard } from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <QueryProvider>
      <Layout>
        <Dashboard />
      </Layout>
    </QueryProvider>
  );
}

export default App;
