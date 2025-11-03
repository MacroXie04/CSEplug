import { Route, Routes } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import QuestionBank from './pages/QuestionBank';
import Grading from './pages/Grading';

function App() {
  return (
    <div className="app-root">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/questions/:courseId" element={<QuestionBank />} />
        <Route path="/grading/:assignmentId" element={<Grading />} />
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </div>
  );
}

export default App;

