import { useParams } from 'react-router-dom';

function QuestionBank() {
  const { courseId } = useParams<{ courseId: string }>();

  return (
    <div className="container py-4">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <h4 className="fw-semibold mb-3">Question Bank</h4>
          <p className="text-muted">Manage free response and multiple choice questions for course {courseId}.</p>
          <p className="text-info">Full implementation coming soon.</p>
        </div>
      </div>
    </div>
  );
}

export default QuestionBank;

