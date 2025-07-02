
-- Create the Database
CREATE DATABASE HospitalReservationDB;
GO

USE HospitalReservationDB;
GO

-- Users Table
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(50) UNIQUE NOT NULL,
    Password NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100)
);
GO

-- Rooms Table
CREATE TABLE Rooms (
    RoomID INT IDENTITY(1,1) PRIMARY KEY,
    RoomNumber NVARCHAR(10) NOT NULL UNIQUE,
    RoomType NVARCHAR(50),
    Price DECIMAL(10, 2),
    Status NVARCHAR(50)
);
GO

-- Reservations Table
CREATE TABLE Reservations (
    ReservationID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT FOREIGN KEY REFERENCES Users(UserID),
    RoomID INT FOREIGN KEY REFERENCES Rooms(RoomID),
    CheckInDate DATE,
    CheckOutDate DATE,
    Status NVARCHAR(50) DEFAULT 'Pending'
);
GO

-- =======================================
-- Stored Procedure: Register User
-- =======================================
GO
CREATE PROCEDURE RegisterUser
    @Username NVARCHAR(50),
    @Password NVARCHAR(100),
    @Email NVARCHAR(100)
AS
BEGIN
    INSERT INTO Users (Username, Password, Email)
    VALUES (@Username, @Password, @Email);
END
GO

-- =======================================
-- Stored Procedure: User Login
-- =======================================
GO
CREATE PROCEDURE UserLogin
    @Username NVARCHAR(50),
    @Password NVARCHAR(100)
AS
BEGIN
    SELECT * FROM Users
    WHERE Username = @Username AND Password = @Password;
END
GO

-- =======================================
-- Stored Procedure: Register Room
-- =======================================
GO
CREATE PROCEDURE RegisterRoom
    @RoomNumber NVARCHAR(10),
    @RoomType NVARCHAR(50),
    @Price DECIMAL(10, 2),
    @Status NVARCHAR(50)
AS
BEGIN
    INSERT INTO Rooms (RoomNumber, RoomType, Price, Status)
    VALUES (@RoomNumber, @RoomType, @Price, @Status);
END
GO

-- =======================================
-- Stored Procedure: Check Room Availability
-- =======================================
GO
CREATE PROCEDURE CheckRoomAvailability
    @RoomID INT,
    @CheckIn DATE,
    @CheckOut DATE
AS
BEGIN
    IF EXISTS (
        SELECT 1 FROM Reservations
        WHERE RoomID = @RoomID
        AND Status <> 'Cancelled'
        AND (
            (@CheckIn BETWEEN CheckInDate AND CheckOutDate)
            OR (@CheckOut BETWEEN CheckInDate AND CheckOutDate)
            OR (CheckInDate BETWEEN @CheckIn AND @CheckOut)
        )
    )
        SELECT 'Not Available';
    ELSE
        SELECT 'Available';
END
GO

-- =======================================
-- Stored Procedure: Make Reservation
-- =======================================
GO
CREATE PROCEDURE MakeReservation
    @UserID INT,
    @RoomID INT,
    @CheckIn DATE,
    @CheckOut DATE
AS
BEGIN
    INSERT INTO Reservations (UserID, RoomID, CheckInDate, CheckOutDate, Status)
    VALUES (@UserID, @RoomID, @CheckIn, @CheckOut, 'Confirmed');
END
GO

-- =======================================
-- Stored Procedure: Generate Bill by Username and RoomNumber
-- =======================================
GO
CREATE PROCEDURE GenerateBillByUserAndRoom
    @Username NVARCHAR(50),
    @RoomNumber NVARCHAR(10)
AS
BEGIN
    DECLARE @UserID INT, @RoomID INT, @Price DECIMAL(10,2), @CheckIn DATE, @CheckOut DATE;

    SELECT @UserID = UserID FROM Users WHERE Username = @Username;
    SELECT @RoomID = RoomID, @Price = Price FROM Rooms WHERE RoomNumber = @RoomNumber;

    SELECT TOP 1 @CheckIn = CheckInDate, @CheckOut = CheckOutDate
    FROM Reservations
    WHERE UserID = @UserID AND RoomID = @RoomID AND Status = 'Confirmed'
    ORDER BY ReservationID DESC;

    DECLARE @Nights INT = DATEDIFF(DAY, @CheckIn, @CheckOut);

    SELECT @Nights * @Price AS BillAmount;
END
GO

-- =======================================
-- Stored Procedure: Update Reservation Status
-- =======================================
GO
CREATE PROCEDURE UpdateReservationStatus
    @ReservationID INT,
    @NewStatus NVARCHAR(50)
AS
BEGIN
    UPDATE Reservations
    SET Status = @NewStatus
    WHERE ReservationID = @ReservationID;
END
GO
