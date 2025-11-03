import { useParams } from 'react-router-dom';

function Grading() {
  const { assignmentId } = useParams<{ assignmentId: string }>();

  return (
    <div className="container py-4">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <h4 className="fw-semibold mb-3">Grading Interface</h4>
          <p className="text-muted">Review and grade submissions for assignment {assignmentId}.</p>
          <p className="text-info">Full implementation coming soon.</p>
        </div>
      </div>
    </div>
  );
}

export default Grading;

