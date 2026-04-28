import type { Course } from "../../types";
import { Link } from "react-router-dom";
import styles from "./CourseCard.module.scss";

interface Props {
  course: Course;
}

const CourseCard = ({ course }: Props) => {
  return (
    <Link to={`/courses/${course.id}`} className={styles.cardLink}>
      <div className={styles.card}>
        <div className={styles.cardTop}>
          {course.cover ? (
            <img src={course.cover} alt={course.title} />
          ) : (
            <div className={styles.placeholder}>📚</div>
          )}

          {course.level && (
            <span className={styles.badge}>{course.level.name}</span>
          )}
        </div>

        <div className={styles.cardBody}>
          <h3 className={styles.title}>{course.title}</h3>
          <p className={styles.description}>{course.description}</p>

          <div className={styles.meta}>
            <span>📖 {course.lessons_count ?? 0} уроков</span>
            <span>👥 {course.students_count ?? 0} студентов</span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default CourseCard;
