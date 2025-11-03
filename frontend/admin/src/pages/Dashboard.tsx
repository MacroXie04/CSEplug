import { gql, useQuery } from '@apollo/client';

const DASHBOARD_QUERY = gql`
  query TeacherDashboard {
    userCoursesConnection {
      id
      role
      course {
        id
        title
        description
      }
    }
  }
`;

function Dashboard() {
  const { data, loading } = useQuery(DASHBOARD_QUERY);

  return (
    <div className="container py-4">
      <div className="row g-4">
        <div className="col-12">
          <h2 className="fw-semibold mb-1">Teacher Dashboard</h2>
          <p className="text-muted">Manage your courses and assignments.</p>
        </div>

        <div className="col-12">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h5 className="card-title mb-3">Your Courses</h5>
              {loading ? (
                <div className="text-center py-5">
                  <div className="spinner-border text-primary" />
                </div>
              ) : (
                <div className="row g-3">
                  {(data?.userCoursesConnection ?? [])
                    .filter((m: any) => m.role === 'instructor' || m.role === 'teaching_assistant')
                    .map((membership: any) => (
                      <div key={membership.id} className="col-md-4">
                        <div className="card h-100 border">
                          <div className="card-body">
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              <h6 className="card-title mb-0">{membership.course.title}</h6>
                              <span className="badge bg-primary text-uppercase">{membership.role}</span>
                            </div>
                            <p className="text-muted small">{membership.course.description || 'No description'}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

