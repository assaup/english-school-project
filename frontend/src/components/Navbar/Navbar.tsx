import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/useAuth";
import { useState } from "react";
import Button from "../Button/Button";
import styles from "./Navbar.module.scss";

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    
    const [isOpen, setIsOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    const closeMenu = () => {
        setIsOpen(false);
    };

    return (
        <header className={styles.header}>
            <div className={styles.container}>
                <Link to="/" className={styles.logo} onClick={closeMenu}>
                    🎓 ENGLOBE
                </Link>

                <button
                    className={styles.burger}
                    onClick={() => setIsOpen((prev) => !prev)}
                    aria-label="Открыть меню"
                    aria-expanded={isOpen}
                >
                    <span></span>
                    <span></span>
                    <span></span>
                </button>

                <div
                    className={`${styles.mobileMenu} ${isOpen ? styles.mobileMenu_open : ""}`}
                >
                    <nav className={styles.nav}>
                        <select
                            name="clients"
                            className={`${styles.navLink} ${styles.navLink__select}`}
                            aria-label="Целевая аудитория курсов"
                        >
                            <option value="">Для взрослых</option>
                            <option value="">Для детей и подростков</option>
                            <option value="">Премиальный тариф</option>
                            <option value="">Для компаний</option>
                            <option value="">Видеокурсы</option>
                        </select>

                        <Link
                            to="/admin/users"
                            className={styles.navLink}
                            onClick={closeMenu}
                        >
                            Преподаватели
                        </Link>

                        <Link to="/courses" className={styles.navLink} onClick={closeMenu}>
                            Курсы
                        </Link>

                        <Link to="/" className={styles.navLink} onClick={closeMenu}>
                            Стоимость
                        </Link>
                    </nav>

                    <div className={styles.buttons}>
                        {user ? (
                            <>
                                <Link
                                    to="/dashboard"
                                    className={styles.navLink}
                                    onClick={closeMenu}
                                >
                                    {user.first_name || user.username}
                                </Link>

                                <Button
                                    type="button"
                                    onClick={handleLogout}
                                    className={styles.button}
                                >
                                    Выйти
                                </Button>
                            </>
                        ) : (
                            <>
                                <Link
                                    to="/login"
                                    className={styles.navLink}
                                    onClick={closeMenu}
                                >
                                    Войти
                                </Link>

                                <Link
                                    to="/register"
                                    className={styles.navLink}
                                    onClick={closeMenu}
                                >
                                    Регистрация
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Navbar;
